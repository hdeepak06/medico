from django.db import models
from django.utils import timezone
import datetime

class DoctorSchedule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField(default=datetime.time(9, 0))
    end_time = models.TimeField(default=datetime.time(17, 0))
    slot_duration = models.IntegerField(default=30, help_text="Slot duration in minutes")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ('doctor', 'day_of_week')

    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK).get(self.day_of_week, '')
        return f"{self.doctor.display_name} - {day_name} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REJECTED = 'REJECTED', 'Rejected'

    class ConsultationType(models.TextChoices):
        IN_PERSON = 'IN_PERSON', 'In-Person Consultation'
        VIDEO = 'VIDEO', 'Online Video Consultation'

    patient = models.ForeignKey('accounts.PatientProfile', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    consultation_type = models.CharField(max_length=20, choices=ConsultationType.choices, default=ConsultationType.IN_PERSON)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    reason_for_visit = models.CharField(max_length=255)
    symptoms = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date', 'appointment_time']

    @property
    def is_past(self):
        appointment_datetime = datetime.datetime.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime < datetime.datetime.now()

    @property
    def can_cancel(self):
        return self.status in [self.Status.PENDING, self.Status.CONFIRMED] and not self.is_past

    @property
    def formatted_time(self):
        return self.appointment_time.strftime("%I:%M %p")

    @property
    def formatted_date(self):
        return self.appointment_date.strftime("%b %d, %Y (%A)")

    def __str__(self):
        return f"Appt #{self.id}: {self.patient.user.full_name} with {self.doctor.display_name} on {self.appointment_date}"


class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    patient = models.ForeignKey('accounts.PatientProfile', on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE, related_name='prescriptions')
    diagnosis = models.CharField(max_length=255)
    medicines = models.JSONField(default=list, help_text="List of medication objects {name, dosage, frequency, duration, instructions}")
    clinical_notes = models.TextField(blank=True)
    lifestyle_advice = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Rx for {self.patient.user.full_name} by {self.doctor.display_name} - {self.diagnosis}"


class Review(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    doctor = models.ForeignKey('accounts.DoctorProfile', on_delete=models.CASCADE, related_name='reviews')
    patient = models.ForeignKey('accounts.PatientProfile', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.patient.user.full_name} for {self.doctor.display_name} ({self.rating}/5)"
