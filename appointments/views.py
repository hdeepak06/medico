from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
import datetime

from accounts.models import DoctorProfile, PatientProfile
from .models import Appointment, Prescription, Review

@login_required
def book_appointment(request, doctor_id=None):
    # Verify user is a patient or has a patient profile
    if not hasattr(request.user, 'patient_profile'):
        if request.user.is_doctor:
            messages.warning(request, "You are logged in as a Doctor. Please log in with a Patient account to book an appointment.")
            return redirect('doctor_dashboard')
        elif request.user.is_medico_admin:
            messages.warning(request, "Administrators cannot book patient appointments directly. Please use a patient account.")
            return redirect('admin_dashboard')
        else:
            # Create a patient profile if missing
            PatientProfile.objects.create(user=request.user)

    patient = request.user.patient_profile
    selected_doctor = None
    if doctor_id:
        selected_doctor = get_object_or_404(DoctorProfile, pk=doctor_id, is_verified=True)

    doctors = DoctorProfile.objects.filter(is_verified=True, is_available=True).select_related('user', 'specialization')

    if request.method == 'POST':
        doc_id = request.POST.get('doctor_id') or doctor_id
        doctor = get_object_or_404(DoctorProfile, pk=doc_id)
        
        date_str = request.POST.get('appointment_date')
        time_str = request.POST.get('appointment_time')
        consultation_type = request.POST.get('consultation_type', Appointment.ConsultationType.IN_PERSON)
        reason = request.POST.get('reason_for_visit', '').strip()
        symptoms = request.POST.get('symptoms', '').strip()

        # Server-side validations
        if not date_str or not time_str or not reason:
            messages.error(request, "Please select an appointment date, available time slot, and reason for visit.")
            return render(request, 'appointments/book.html', {
                'selected_doctor': doctor,
                'doctors': doctors,
            })

        try:
            appt_date = datetime.date.fromisoformat(date_str)
            time_parts = [int(p) for p in time_str.split(':')[:2]]
            appt_time = datetime.time(time_parts[0], time_parts[1])
        except (ValueError, IndexError):
            messages.error(request, "Invalid date or time slot selected.")
            return redirect('book_appointment', doctor_id=doctor.id)

        # 1. Date cannot be in the past
        now = datetime.datetime.now()
        appt_dt = datetime.datetime.combine(appt_date, appt_time)
        if appt_dt < now:
            messages.error(request, "Cannot book an appointment in the past. Please select an upcoming date and time.")
            return redirect('book_appointment', doctor_id=doctor.id)

        # 2. Prevent double-booking for the same doctor at the same slot
        conflict = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appt_date,
            appointment_time=appt_time
        ).exclude(
            status__in=[Appointment.Status.CANCELLED, Appointment.Status.REJECTED]
        ).exists()

        if conflict:
            messages.error(request, f"Sorry, {doctor.display_name} is already booked at {appt_time.strftime('%I:%M %p')} on {appt_date}. Please choose another time slot.")
            return redirect('book_appointment', doctor_id=doctor.id)

        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=appt_date,
            appointment_time=appt_time,
            consultation_type=consultation_type,
            status=Appointment.Status.CONFIRMED,
            reason_for_visit=reason,
            symptoms=symptoms
        )

        messages.success(request, f"Appointment successfully booked with {doctor.display_name} on {appt_date.strftime('%b %d, %Y')} at {appt_time.strftime('%I:%M %p')}!")
        return redirect('appointment_detail', pk=appointment.id)

    # Next 14 days dates for easy UI selection
    today = datetime.date.today()
    min_date = today.isoformat()
    max_date = (today + datetime.timedelta(days=30)).isoformat()

    return render(request, 'appointments/book.html', {
        'selected_doctor': selected_doctor,
        'doctors': doctors,
        'min_date': min_date,
        'max_date': max_date,
    })


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient__user', 'doctor__user', 'doctor__specialization'),
        pk=pk
    )

    # Access control: only the patient, the doctor, or an admin can view
    user = request.user
    is_owner_patient = hasattr(user, 'patient_profile') and (appointment.patient == user.patient_profile)
    is_owner_doctor = hasattr(user, 'doctor_profile') and (appointment.doctor == user.doctor_profile)

    if not (is_owner_patient or is_owner_doctor or user.is_medico_admin):
        return HttpResponseForbidden("You do not have permission to view this appointment record.")

    existing_review = None
    if appointment.status == Appointment.Status.COMPLETED and hasattr(user, 'patient_profile'):
        existing_review = Review.objects.filter(appointment=appointment, patient=user.patient_profile).first()

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'is_patient': is_owner_patient,
        'is_doctor': is_owner_doctor,
        'is_admin': user.is_medico_admin,
        'existing_review': existing_review,
    })


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user

    is_owner_patient = hasattr(user, 'patient_profile') and (appointment.patient == user.patient_profile)
    is_owner_doctor = hasattr(user, 'doctor_profile') and (appointment.doctor == user.doctor_profile)

    if not (is_owner_patient or is_owner_doctor or user.is_medico_admin):
        return HttpResponseForbidden("You do not have permission to cancel this appointment.")

    if appointment.status == Appointment.Status.COMPLETED:
        messages.error(request, "Completed appointments cannot be cancelled.")
        return redirect('appointment_detail', pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('cancellation_reason', 'Cancelled by user request.')
        appointment.status = Appointment.Status.CANCELLED
        appointment.cancellation_reason = reason
        appointment.save()

        messages.info(request, f"Appointment #{appointment.id} has been cancelled successfully.")
        if is_owner_doctor:
            return redirect('doctor_dashboard')
        return redirect('patient_dashboard')

    return render(request, 'appointments/cancel_confirm.html', {'appointment': appointment})


@login_required
def reschedule_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user

    is_owner_patient = hasattr(user, 'patient_profile') and (appointment.patient == user.patient_profile)
    if not (is_owner_patient or user.is_medico_admin):
        return HttpResponseForbidden("Only the patient can reschedule this appointment.")

    if appointment.status == Appointment.Status.COMPLETED:
        messages.error(request, "Completed appointments cannot be rescheduled.")
        return redirect('appointment_detail', pk=pk)

    if request.method == 'POST':
        new_date_str = request.POST.get('appointment_date')
        new_time_str = request.POST.get('appointment_time')

        if not new_date_str or not new_time_str:
            messages.error(request, "Please choose a valid date and available time slot.")
            return redirect('reschedule_appointment', pk=pk)

        try:
            new_date = datetime.date.fromisoformat(new_date_str)
            time_parts = [int(p) for p in new_time_str.split(':')[:2]]
            new_time = datetime.time(time_parts[0], time_parts[1])
        except (ValueError, IndexError):
            messages.error(request, "Invalid date/time format.")
            return redirect('reschedule_appointment', pk=pk)

        # Check not in past
        if datetime.datetime.combine(new_date, new_time) < datetime.datetime.now():
            messages.error(request, "Cannot reschedule to a past date/time.")
            return redirect('reschedule_appointment', pk=pk)

        # Check collision
        collision = Appointment.objects.filter(
            doctor=appointment.doctor,
            appointment_date=new_date,
            appointment_time=new_time
        ).exclude(pk=appointment.pk).exclude(
            status__in=[Appointment.Status.CANCELLED, Appointment.Status.REJECTED]
        ).exists()

        if collision:
            messages.error(request, f"That slot ({new_time.strftime('%I:%M %p')}) is already booked with {appointment.doctor.display_name}. Please pick another slot.")
            return redirect('reschedule_appointment', pk=pk)

        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save()

        messages.success(request, f"Appointment successfully rescheduled to {new_date.strftime('%b %d, %Y')} at {new_time.strftime('%I:%M %p')}.")
        return redirect('appointment_detail', pk=pk)

    today = datetime.date.today()
    return render(request, 'appointments/reschedule.html', {
        'appointment': appointment,
        'min_date': today.isoformat(),
        'max_date': (today + datetime.timedelta(days=30)).isoformat(),
    })


@login_required
def prescription_view(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient__user', 'doctor__user', 'doctor__specialization'),
        pk=pk
    )

    user = request.user
    is_owner_patient = hasattr(user, 'patient_profile') and (appointment.patient == user.patient_profile)
    is_owner_doctor = hasattr(user, 'doctor_profile') and (appointment.doctor == user.doctor_profile)

    if not (is_owner_patient or is_owner_doctor or user.is_medico_admin):
        return HttpResponseForbidden("You do not have authorization to view this prescription.")

    try:
        prescription = appointment.prescription
    except Prescription.DoesNotExist:
        messages.warning(request, "No prescription has been issued yet for this appointment.")
        return redirect('appointment_detail', pk=pk)

    return render(request, 'appointments/prescription_view.html', {
        'appointment': appointment,
        'prescription': prescription,
    })


@login_required
def submit_review(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user

    if not hasattr(user, 'patient_profile') or appointment.patient != user.patient_profile:
        return HttpResponseForbidden("Only the patient can review this consultation.")

    if appointment.status != Appointment.Status.COMPLETED:
        messages.error(request, "Reviews can only be submitted after consultation is completed.")
        return redirect('appointment_detail', pk=pk)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()

        if comment:
            Review.objects.update_or_create(
                appointment=appointment,
                doctor=appointment.doctor,
                patient=user.patient_profile,
                defaults={
                    'rating': max(1, min(5, rating)),
                    'comment': comment
                }
            )
            # Recalculate doctor rating
            all_reviews = appointment.doctor.patient_reviews.all()
            if all_reviews.exists():
                total = sum(r.rating for r in all_reviews)
                appointment.doctor.rating = round(total / all_reviews.count(), 2)
                appointment.doctor.reviews_count = all_reviews.count()
                appointment.doctor.save()

            messages.success(request, "Thank you for your feedback! Your review helps other patients.")
        return redirect('appointment_detail', pk=pk)

    return redirect('appointment_detail', pk=pk)
