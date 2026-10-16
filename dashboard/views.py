from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
import datetime
import json

from accounts.models import User, PatientProfile, DoctorProfile
from core.models import Specialization
from appointments.models import Appointment, Prescription, DoctorSchedule

@login_required
def dashboard_dispatch(request):
    user = request.user
    if user.is_medico_admin:
        return redirect('admin_dashboard')
    elif user.is_doctor:
        return redirect('doctor_dashboard')
    elif user.is_patient:
        return redirect('patient_dashboard')
    else:
        return redirect('home')


# ----------------------------------------------------
# PATIENT DASHBOARD
# ----------------------------------------------------
@login_required
def patient_dashboard(request):
    user = request.user
    if not hasattr(user, 'patient_profile'):
        if user.is_doctor:
            return redirect('doctor_dashboard')
        if user.is_medico_admin:
            return redirect('admin_dashboard')
        PatientProfile.objects.create(user=user)

    patient = user.patient_profile
    today = datetime.date.today()

    all_appts = Appointment.objects.filter(patient=patient).select_related('doctor__user', 'doctor__specialization')

    upcoming_appointments = all_appts.filter(
        appointment_date__gte=today
    ).exclude(
        status__in=[Appointment.Status.CANCELLED, Appointment.Status.REJECTED]
    ).order_by('appointment_date', 'appointment_time')

    past_appointments = all_appts.filter(
        Q(appointment_date__lt=today) | Q(status__in=[Appointment.Status.COMPLETED, Appointment.Status.CANCELLED])
    ).order_by('-appointment_date', '-appointment_time')

    prescriptions = Prescription.objects.filter(patient=patient).select_related('doctor__user', 'appointment').order_by('-created_at')

    stats = {
        'total_appointments': all_appts.count(),
        'upcoming_count': upcoming_appointments.count(),
        'completed_count': all_appts.filter(status=Appointment.Status.COMPLETED).count(),
        'prescriptions_count': prescriptions.count(),
    }

    active_tab = request.GET.get('tab', 'overview')

    return render(request, 'dashboard/patient_dashboard.html', {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'prescriptions': prescriptions,
        'stats': stats,
        'active_tab': active_tab,
        'today': today,
    })


# ----------------------------------------------------
# DOCTOR DASHBOARD
# ----------------------------------------------------
@login_required
def doctor_dashboard(request):
    user = request.user
    if not hasattr(user, 'doctor_profile'):
        if user.is_patient:
            return redirect('patient_dashboard')
        return redirect('admin_dashboard')

    doctor = user.doctor_profile
    today = datetime.date.today()

    all_appts = Appointment.objects.filter(doctor=doctor).select_related('patient__user').order_by('-appointment_date', '-appointment_time')

    today_appointments = all_appts.filter(appointment_date=today).exclude(status__in=[Appointment.Status.CANCELLED, Appointment.Status.REJECTED])
    pending_appointments = all_appts.filter(status=Appointment.Status.PENDING)
    confirmed_appointments = all_appts.filter(status=Appointment.Status.CONFIRMED, appointment_date__gte=today)
    completed_appointments = all_appts.filter(status=Appointment.Status.COMPLETED)

    # Schedules
    schedules = doctor.schedules.all().order_by('day_of_week')

    # Status filter from query param
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'pending':
        displayed_appts = pending_appointments
    elif status_filter == 'today':
        displayed_appts = today_appointments
    elif status_filter == 'confirmed':
        displayed_appts = confirmed_appointments
    elif status_filter == 'completed':
        displayed_appts = completed_appointments
    else:
        displayed_appts = all_appts

    stats = {
        'total_appointments': all_appts.count(),
        'today_count': today_appointments.count(),
        'pending_count': pending_appointments.count(),
        'completed_count': completed_appointments.count(),
        'rating': doctor.rating,
        'reviews_count': doctor.reviews_count,
    }

    active_tab = request.GET.get('tab', 'appointments')

    return render(request, 'dashboard/doctor_dashboard.html', {
        'doctor': doctor,
        'stats': stats,
        'displayed_appts': displayed_appts,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'schedules': schedules,
        'status_filter': status_filter,
        'active_tab': active_tab,
        'today': today,
    })


@login_required
def doctor_appointment_action(request, pk, action):
    doctor_profile = getattr(request.user, 'doctor_profile', None)
    if not doctor_profile:
        return HttpResponseForbidden("Only doctors can perform this action.")

    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor_profile)

    if action == 'confirm':
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save()
        messages.success(request, f"Appointment #{appointment.id} with {appointment.patient.user.full_name} confirmed.")
    elif action == 'reject':
        appointment.status = Appointment.Status.REJECTED
        appointment.cancellation_reason = request.POST.get('reason', 'Doctor unavailable.')
        appointment.save()
        messages.info(request, f"Appointment #{appointment.id} was rejected.")

    return redirect('doctor_dashboard')


@login_required
def doctor_complete_appointment(request, pk):
    doctor_profile = getattr(request.user, 'doctor_profile', None)
    if not doctor_profile:
        return HttpResponseForbidden("Only doctors can issue prescriptions.")

    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor_profile)

    if request.method == 'POST':
        diagnosis = request.POST.get('diagnosis', '').strip()
        clinical_notes = request.POST.get('clinical_notes', '').strip()
        lifestyle_advice = request.POST.get('lifestyle_advice', '').strip()
        follow_up_str = request.POST.get('follow_up_date', '')

        # Medication lists parsed from form inputs
        med_names = request.POST.getlist('med_name[]')
        med_dosages = request.POST.getlist('med_dosage[]')
        med_frequencies = request.POST.getlist('med_frequency[]')
        med_durations = request.POST.getlist('med_duration[]')
        med_instructions = request.POST.getlist('med_instructions[]')

        medicines = []
        for i in range(len(med_names)):
            name = med_names[i].strip()
            if name:
                medicines.append({
                    'name': name,
                    'dosage': med_dosages[i].strip() if i < len(med_dosages) else '',
                    'frequency': med_frequencies[i].strip() if i < len(med_frequencies) else '',
                    'duration': med_durations[i].strip() if i < len(med_durations) else '',
                    'instructions': med_instructions[i].strip() if i < len(med_instructions) else '',
                })

        follow_up_date = None
        if follow_up_str:
            try:
                follow_up_date = datetime.date.fromisoformat(follow_up_str)
            except ValueError:
                pass

        # Update appointment status to COMPLETED
        appointment.status = Appointment.Status.COMPLETED
        if clinical_notes:
            appointment.doctor_notes = clinical_notes
        appointment.save()

        # Create or update prescription
        Prescription.objects.update_or_create(
            appointment=appointment,
            defaults={
                'patient': appointment.patient,
                'doctor': doctor_profile,
                'diagnosis': diagnosis or 'General Consultation Examination',
                'medicines': medicines,
                'clinical_notes': clinical_notes,
                'lifestyle_advice': lifestyle_advice,
                'follow_up_date': follow_up_date,
            }
        )

        messages.success(request, f"Appointment #{appointment.id} marked as Completed. Digital prescription has been created.")
        return redirect('doctor_dashboard')

    return render(request, 'dashboard/doctor_write_prescription.html', {
        'appointment': appointment,
        'today': datetime.date.today().isoformat(),
    })


@login_required
def doctor_toggle_availability(request):
    doctor_profile = getattr(request.user, 'doctor_profile', None)
    if not doctor_profile:
        return HttpResponseForbidden()

    doctor_profile.is_available = not doctor_profile.is_available
    doctor_profile.save()
    status_str = "Available for bookings" if doctor_profile.is_available else "Marked as Away/Unavailable"
    messages.info(request, f"Your status updated: {status_str}.")
    return redirect('doctor_dashboard')


# ----------------------------------------------------
# ADMIN DASHBOARD
# ----------------------------------------------------
@login_required
def admin_dashboard(request):
    if not request.user.is_medico_admin:
        return HttpResponseForbidden("Administrator access required.")

    today = datetime.date.today()

    total_patients = User.objects.filter(role=User.Role.PATIENT).count()
    total_doctors = DoctorProfile.objects.count()
    pending_verifications = DoctorProfile.objects.filter(is_verified=False).count()
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    completed_appointments = Appointment.objects.filter(status=Appointment.Status.COMPLETED).count()

    # Doctors list
    doctors_list = DoctorProfile.objects.select_related('user', 'specialization').order_by('-created_at')

    # Appointments list with search/filter
    appointments_qs = Appointment.objects.select_related('patient__user', 'doctor__user', 'doctor__specialization').order_by('-appointment_date', '-appointment_time')
    status_filter = request.GET.get('status')
    if status_filter:
        appointments_qs = appointments_qs.filter(status=status_filter)

    # Specializations
    specialties = Specialization.objects.annotate(doc_count=Count('doctors')).all()

    # User directory
    user_search = request.GET.get('user_q', '').strip()
    users_qs = User.objects.all().order_by('-date_joined')
    if user_search:
        users_qs = users_qs.filter(
            Q(username__icontains=user_search) |
            Q(first_name__icontains=user_search) |
            Q(last_name__icontains=user_search) |
            Q(email__icontains=user_search)
        )

    # Paginate appointments
    paginator = Paginator(appointments_qs, 10)
    page_number = request.GET.get('page')
    appointments_page = paginator.get_page(page_number)

    active_tab = request.GET.get('tab', 'overview')

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'pending_verifications': pending_verifications,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'completed_appointments': completed_appointments,
        'doctors_list': doctors_list,
        'appointments_page': appointments_page,
        'specialties': specialties,
        'users': users_qs[:20],
        'active_tab': active_tab,
        'status_filter': status_filter,
    })


@login_required
def admin_toggle_doctor_verification(request, pk):
    if not request.user.is_medico_admin:
        return HttpResponseForbidden()

    doctor = get_object_or_404(DoctorProfile, pk=pk)
    doctor.is_verified = not doctor.is_verified
    doctor.save()

    status = "Verified" if doctor.is_verified else "Unverified / Pending"
    messages.success(request, f"{doctor.display_name} has been set to: {status}.")
    return redirect(f"{redirect('admin_dashboard').url}?tab=doctors")


@login_required
def admin_toggle_user_active(request, user_id):
    if not request.user.is_medico_admin:
        return HttpResponseForbidden()

    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot deactivate your own administrative account.")
        return redirect(f"{redirect('admin_dashboard').url}?tab=users")

    target_user.is_active = not target_user.is_active
    target_user.save()

    status = "Active" if target_user.is_active else "Deactivated"
    messages.info(request, f"User {target_user.username} is now {status}.")
    return redirect(f"{redirect('admin_dashboard').url}?tab=users")


@login_required
def admin_add_specialization(request):
    if not request.user.is_medico_admin:
        return HttpResponseForbidden()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        icon_name = request.POST.get('icon_name', 'stethoscope')
        color = request.POST.get('color_accent', '#0284C7')

        if name and description:
            Specialization.objects.create(
                name=name,
                description=description,
                icon_name=icon_name,
                color_accent=color,
                is_featured=True
            )
            messages.success(request, f"Specialization '{name}' added successfully.")
        else:
            messages.error(request, "Please provide specialization name and description.")

    return redirect(f"{redirect('admin_dashboard').url}?tab=specialties")


@login_required
def admin_delete_specialization(request, pk):
    if not request.user.is_medico_admin:
        return HttpResponseForbidden()

    spec = get_object_or_404(Specialization, pk=pk)
    name = spec.name
    spec.delete()
    messages.info(request, f"Specialization '{name}' has been removed.")
    return redirect(f"{redirect('admin_dashboard').url}?tab=specialties")
