from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import datetime
from accounts.models import DoctorProfile, PatientProfile
from core.models import Specialization
from appointments.models import Appointment, DoctorSchedule, Prescription

User = get_user_model()

class MedicoSystemTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Specialty
        self.specialty = Specialization.objects.create(
            name="Cardiology",
            slug="cardiology",
            description="Heart care"
        )

        # Doctor
        self.doctor_user = User.objects.create_user(
            username="test_doctor",
            email="doctor@medico.com",
            password="testpassword123",
            first_name="Marcus",
            last_name="Welby",
            role=User.Role.DOCTOR
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization=self.specialty,
            qualification="MBBS, MD",
            experience_years=10,
            consultation_fee=75.00,
            is_verified=True,
            is_available=True
        )

        # Patient
        self.patient_user = User.objects.create_user(
            username="test_patient",
            email="patient@example.com",
            password="testpassword123",
            first_name="Jane",
            last_name="Doe",
            role=User.Role.PATIENT
        )
        self.patient = PatientProfile.objects.create(
            user=self.patient_user,
            blood_group="O+",
            city="New York"
        )

        # Admin
        self.admin_user = User.objects.create_superuser(
            username="test_admin",
            email="admin@medico.com",
            password="testpassword123",
            role=User.Role.ADMIN
        )

    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Health,")
        self.assertContains(response, "Cardiology")

    def test_doctor_list_and_search(self):
        response = self.client.get(reverse('doctor_list') + '?q=Welby')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Marcus Welby")

    def test_appointment_booking_and_double_booking_prevention(self):
        self.client.login(username="test_patient", password="testpassword123")
        target_date = datetime.date.today() + datetime.timedelta(days=2)
        target_time = "10:30"

        # 1. Book first appointment
        post_data = {
            'doctor_id': self.doctor.id,
            'appointment_date': target_date.isoformat(),
            'appointment_time': target_time,
            'consultation_type': 'IN_PERSON',
            'reason_for_visit': 'General consultation',
            'symptoms': 'None'
        }
        res1 = self.client.post(reverse('book_appointment', args=[self.doctor.id]), post_data, follow=True)
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(Appointment.objects.filter(doctor=self.doctor, appointment_date=target_date, appointment_time="10:30:00").exists())

        # 2. Try booking the exact same doctor and slot (Must prevent double-booking)
        res2 = self.client.post(reverse('book_appointment', args=[self.doctor.id]), post_data, follow=True)
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, "already booked")

    def test_role_based_dashboard_access(self):
        # Patient login
        self.client.login(username="test_patient", password="testpassword123")
        res = self.client.get(reverse('dashboard_dispatch'), follow=True)
        self.assertContains(res, "Patient Portal")

        # Doctor cannot view patient dashboard directly as doctor
        self.client.login(username="test_doctor", password="testpassword123")
        res_doc = self.client.get(reverse('dashboard_dispatch'), follow=True)
        self.assertContains(res_doc, "Doctor Practice Portal")
