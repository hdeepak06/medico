from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        DOCTOR = 'DOCTOR', 'Doctor'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    phone = models.CharField(max_length=30, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    avatar_url = models.CharField(max_length=255, blank=True)

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_medico_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser or self.is_staff

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.username

    def get_avatar(self):
        if self.profile_picture:
            return self.profile_picture.url
        if self.avatar_url:
            return self.avatar_url
        if self.is_doctor:
            return "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&auto=format&fit=crop&q=80"
        return "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80"

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"


class PatientProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, default='Male')
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUPS, blank=True, default='O+')
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True, default='New York')
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)
    allergies = models.TextField(blank=True, help_text="e.g. Penicillin, Peanuts")
    chronic_conditions = models.TextField(blank=True, help_text="e.g. Hypertension, Asthma")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Patient: {self.user.full_name}"


class DoctorProfile(models.Model):
    CONSULTATION_TYPES = [
        ('BOTH', 'In-Person & Online Video'),
        ('IN_PERSON', 'In-Person Only'),
        ('VIDEO', 'Online Video Only'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.ForeignKey('core.Specialization', on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    title = models.CharField(max_length=30, default='Dr.')
    license_number = models.CharField(max_length=50, blank=True)
    qualification = models.CharField(max_length=200, default='MBBS, MD')
    experience_years = models.PositiveIntegerField(default=7)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=65.00)
    hospital_name = models.CharField(max_length=200, default='Medico Central Hospital')
    clinic_address = models.TextField(blank=True, default='Suite 402, Medico Plaza, New York, NY')
    city = models.CharField(max_length=100, default='New York')
    bio = models.TextField(blank=True, default='Dedicated healthcare professional committed to patient-first medical excellence and holistic care.')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.9)
    reviews_count = models.PositiveIntegerField(default=148)
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPES, default='BOTH')
    is_verified = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', '-experience_years']

    @property
    def display_name(self):
        return f"{self.title} {self.user.full_name}"

    def get_photo(self):
        return self.user.get_avatar()

    def __str__(self):
        spec = self.specialization.name if self.specialization else "General"
        return f"{self.display_name} ({spec})"
