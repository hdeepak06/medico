from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
import datetime

from accounts.models import DoctorProfile, User
from .models import Specialization, Testimonial, ContactMessage
from appointments.models import DoctorSchedule, Appointment

def home(request):
    specialties = Specialization.objects.annotate(doc_count=Count('doctors')).filter(is_featured=True)[:8]
    featured_doctors = DoctorProfile.objects.filter(is_verified=True, is_available=True).select_related('user', 'specialization')[:6]
    testimonials = Testimonial.objects.filter(is_featured=True)[:3]

    stats = {
        'doctors_count': DoctorProfile.objects.filter(is_verified=True).count(),
        'patients_count': User.objects.filter(role=User.Role.PATIENT).count() + 15200,
        'specialties_count': Specialization.objects.count(),
        'satisfaction_rate': '99.4%',
    }

    return render(request, 'core/home.html', {
        'specialties': specialties,
        'featured_doctors': featured_doctors,
        'testimonials': testimonials,
        'stats': stats,
    })


def doctor_list(request):
    doctors = DoctorProfile.objects.filter(is_verified=True).select_related('user', 'specialization')

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        doctors = doctors.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(specialization__name__icontains=q) |
            Q(hospital_name__icontains=q) |
            Q(city__icontains=q) |
            Q(qualification__icontains=q)
        )

    # Specialization filter
    specialty_slug = request.GET.get('specialty')
    selected_specialty = None
    if specialty_slug:
        selected_specialty = get_object_or_404(Specialization, slug=specialty_slug)
        doctors = doctors.filter(specialization=selected_specialty)

    # Consultation type
    ctype = request.GET.get('type')
    if ctype in ['IN_PERSON', 'VIDEO']:
        doctors = doctors.filter(Q(consultation_type=ctype) | Q(consultation_type='BOTH'))

    # Availability filter
    available = request.GET.get('available')
    if available == '1':
        doctors = doctors.filter(is_available=True)

    # Sorting
    sort = request.GET.get('sort', 'rating')
    if sort == 'fee_asc':
        doctors = doctors.order_by('consultation_fee')
    elif sort == 'fee_desc':
        doctors = doctors.order_by('-consultation_fee')
    elif sort == 'exp':
        doctors = doctors.order_by('-experience_years')
    else:
        doctors = doctors.order_by('-rating', '-experience_years')

    all_specialties = Specialization.objects.annotate(doc_count=Count('doctors')).all()

    # Pagination: 6 doctors per page
    paginator = Paginator(doctors, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/doctors.html', {
        'page_obj': page_obj,
        'doctors': page_obj.object_list,
        'all_specialties': all_specialties,
        'selected_specialty': selected_specialty,
        'search_query': q,
        'selected_type': ctype,
        'selected_sort': sort,
        'total_count': paginator.count,
    })


def doctor_detail(request, pk):
    doctor = get_object_or_404(DoctorProfile.objects.select_related('user', 'specialization'), pk=pk)
    schedules = doctor.schedules.filter(is_active=True).order_by('day_of_week')
    reviews = doctor.patient_reviews.select_related('patient__user').order_by('-created_at')[:10]

    # Calculate 7 upcoming booking dates
    today = datetime.date.today()
    upcoming_dates = []
    active_days = set(schedules.values_list('day_of_week', flat=True))

    for i in range(1, 15):
        d = today + datetime.timedelta(days=i)
        # Check if doctor has schedule on this weekday (0=Mon, 6=Sun)
        if d.weekday() in active_days or not active_days:
            upcoming_dates.append(d)
        if len(upcoming_dates) >= 7:
            break

    return render(request, 'core/doctor_detail.html', {
        'doctor': doctor,
        'schedules': schedules,
        'reviews': reviews,
        'upcoming_dates': upcoming_dates,
    })


def specialty_list(request):
    specialties = Specialization.objects.annotate(doc_count=Count('doctors')).all()
    return render(request, 'core/specialties.html', {'specialties': specialties})


def specialty_detail(request, slug):
    specialty = get_object_or_404(Specialization, slug=slug)
    doctors = DoctorProfile.objects.filter(specialization=specialty, is_verified=True).select_related('user')
    return render(request, 'core/specialty_detail.html', {
        'specialty': specialty,
        'doctors': doctors,
    })


def about_us(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, "Thank you for reaching out! Our medical desk will respond within 24 hours.")
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'core/contact.html')


def api_doctor_slots(request, doctor_id):
    """API endpoint to get available and booked slots for a given doctor on a specific date."""
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'error': 'Date is required (YYYY-MM-DD)'}, status=400)

    try:
        query_date = datetime.date.fromisoformat(date_str)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    # Check if date is in the past
    if query_date < datetime.date.today():
        return JsonResponse({'slots': [], 'message': 'Date is in the past', 'is_past': True})

    # Find doctor schedule for this day of week
    weekday = query_date.weekday()
    schedule = doctor.schedules.filter(day_of_week=weekday, is_active=True).first()

    slots = []
    if schedule:
        start = schedule.start_time
        end = schedule.end_time
        slot_min = schedule.slot_duration or 30

        current = datetime.datetime.combine(query_date, start)
        end_dt = datetime.datetime.combine(query_date, end)

        now = datetime.datetime.now()

        while current + datetime.timedelta(minutes=slot_min) <= end_dt:
            time_val = current.time()
            time_str = time_val.strftime("%H:%M")
            display_str = current.strftime("%I:%M %p")

            # Do not allow booking time that has already passed today
            is_time_past = (query_date == datetime.date.today() and current <= now)

            slots.append({
                'value': time_str,
                'display': display_str,
                'is_past': is_time_past
            })
            current += datetime.timedelta(minutes=slot_min)
    else:
        # Fallback default slots if no custom schedule was set
        default_times = [
            ("09:00", "09:00 AM"), ("09:30", "09:30 AM"),
            ("10:00", "10:00 AM"), ("10:30", "10:30 AM"),
            ("11:00", "11:00 AM"), ("11:30", "11:30 AM"),
            ("14:00", "02:00 PM"), ("14:30", "02:30 PM"),
            ("15:00", "03:00 PM"), ("15:30", "03:30 PM"),
            ("16:00", "04:00 PM"), ("16:30", "04:30 PM"),
        ]
        now = datetime.datetime.now()
        for t_val, t_disp in default_times:
            hour, minute = map(int, t_val.split(':'))
            slot_dt = datetime.datetime.combine(query_date, datetime.time(hour, minute))
            is_time_past = (query_date == datetime.date.today() and slot_dt <= now)
            slots.append({
                'value': t_val,
                'display': t_disp,
                'is_past': is_time_past
            })

    # Fetch existing appointments for this doctor on this date that are not cancelled
    booked_times = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=query_date
    ).exclude(
        status__in=[Appointment.Status.CANCELLED, Appointment.Status.REJECTED]
    ).values_list('appointment_time', flat=True)

    booked_str_set = {t.strftime("%H:%M") for t in booked_times}

    # Annotate slots with booked status
    for s in slots:
        s['is_booked'] = (s['value'] in booked_str_set)
        s['is_available'] = (not s['is_booked']) and (not s['is_past'])

    return JsonResponse({
        'doctor_name': doctor.display_name,
        'date': date_str,
        'slots': slots,
        'fee': str(doctor.consultation_fee)
    })
