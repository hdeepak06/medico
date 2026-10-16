from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, PatientProfile, DoctorProfile
from .forms import PatientRegistrationForm, DoctorRegistrationForm, PatientProfileUpdateForm, DoctorProfileUpdateForm

def login_view(request):
    # Demo 1-click login handler (allows instant switching between demo roles)
    demo_role = request.GET.get('demo')
    if demo_role:
        demo_map = {
            'admin': 'admin',
            'doctor': 'dr_sarah',
            'patient_john': 'john_patient',
            'patient_emma': 'emma_patient',
        }
        target_username = demo_map.get(demo_role)
        if target_username:
            try:
                user = User.objects.get(username=target_username)
                logout(request)
                login(request, user)
                messages.success(request, f"Welcome to Medico, {user.full_name}! (Logged in as {user.get_role_display()})")
                return redirect('dashboard_dispatch')
            except User.DoesNotExist:
                messages.error(request, "Demo account not found. Please run seed command.")

    if request.user.is_authenticated:
        return redirect('dashboard_dispatch')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard_dispatch')
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely. See you soon!")
    return redirect('home')


def register_patient(request):
    if request.user.is_authenticated:
        return redirect('dashboard_dispatch')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Medico, {user.first_name}! Your patient profile is active.")
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register_patient.html', {'form': form})


def register_doctor(request):
    if request.user.is_authenticated:
        return redirect('dashboard_dispatch')

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome Dr. {user.last_name}! Your doctor profile is now registered.")
            return redirect('doctor_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DoctorRegistrationForm()

    return render(request, 'accounts/register_doctor.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user
    if user.is_patient:
        patient_profile = user.patient_profile
        if request.method == 'POST':
            form = PatientProfileUpdateForm(request.POST, instance=patient_profile)
            if form.is_valid():
                # Update User first/last/phone
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.phone = form.cleaned_data['phone']
                user.save()
                form.save()
                messages.success(request, "Your medical profile has been updated.")
                return redirect('patient_dashboard')
        else:
            initial = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
            }
            form = PatientProfileUpdateForm(instance=patient_profile, initial=initial)
        return render(request, 'accounts/profile.html', {'form': form, 'profile_type': 'patient'})

    elif user.is_doctor:
        doctor_profile = user.doctor_profile
        if request.method == 'POST':
            form = DoctorProfileUpdateForm(request.POST, instance=doctor_profile)
            if form.is_valid():
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.phone = form.cleaned_data['phone']
                user.save()
                form.save()
                messages.success(request, "Your professional doctor profile has been updated.")
                return redirect('doctor_dashboard')
        else:
            initial = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
            }
            form = DoctorProfileUpdateForm(instance=doctor_profile, initial=initial)
        return render(request, 'accounts/profile.html', {'form': form, 'profile_type': 'doctor'})

    else:
        messages.info(request, "Administrator settings are managed via the Admin Dashboard.")
        return redirect('admin_dashboard')
