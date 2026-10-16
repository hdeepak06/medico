from django import forms
from django.contrib.auth import authenticate, login
from .models import User, PatientProfile, DoctorProfile
from core.models import Specialization

class PatientRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email address'}))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Create secure password'}), min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm password'}))
    
    # Profile fields
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}))
    gender = forms.ChoiceField(choices=PatientProfile.GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    blood_group = forms.ChoiceField(choices=PatientProfile.BLOOD_GROUPS, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street Address'}))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choose username'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.PATIENT
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender=self.cleaned_data.get('gender', 'Male'),
                blood_group=self.cleaned_data.get('blood_group', 'O+'),
                address=self.cleaned_data.get('address', ''),
                city=self.cleaned_data.get('city', 'New York'),
            )
        return user


class DoctorRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email address'}))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Create secure password'}), min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm password'}))

    # Doctor specific fields
    specialization = forms.ModelChoiceField(queryset=Specialization.objects.all(), empty_label="Select Specialization", widget=forms.Select(attrs={'class': 'form-input'}))
    qualification = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. MBBS, MD (Cardiology)'}))
    experience_years = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Years of experience'}))
    consultation_fee = forms.DecimalField(max_digits=8, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Consultation Fee ($)'}))
    hospital_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Hospital or Clinic Name'}))
    license_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Medical License Number'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choose username'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.DOCTOR
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data.get('specialization'),
                qualification=self.cleaned_data.get('qualification'),
                experience_years=self.cleaned_data.get('experience_years', 1),
                consultation_fee=self.cleaned_data.get('consultation_fee', 50.00),
                hospital_name=self.cleaned_data.get('hospital_name'),
                license_number=self.cleaned_data.get('license_number'),
                is_verified=True,  # Auto-verified for demo convenience, togglable in Admin
            )
        return user


class PatientProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'gender', 'blood_group', 'address', 'city', 'emergency_contact_name', 'emergency_contact_phone', 'allergies', 'chronic_conditions']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'blood_group': forms.Select(attrs={'class': 'form-input'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-input'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'allergies': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'chronic_conditions': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }


class DoctorProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = DoctorProfile
        fields = ['title', 'specialization', 'qualification', 'experience_years', 'consultation_fee', 'hospital_name', 'clinic_address', 'city', 'bio', 'consultation_type', 'is_available']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'specialization': forms.Select(attrs={'class': 'form-input'}),
            'qualification': forms.TextInput(attrs={'class': 'form-input'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-input'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-input'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-input'}),
            'clinic_address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'consultation_type': forms.Select(attrs={'class': 'form-input'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
