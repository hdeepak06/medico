from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime
from accounts.models import PatientProfile, DoctorProfile
from core.models import Specialization, Testimonial
from appointments.models import DoctorSchedule, Appointment, Prescription, Review

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with realistic medical demo data for Medico'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating Medico database with demo data..."))

        # 1. Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@medico.com',
                'first_name': 'Alexander',
                'last_name': 'Hayes',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone': '+1 (555) 019-2831',
                'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80',
            }
        )
        if created:
            admin_user.set_password('adminpassword123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created Admin: admin / adminpassword123"))

        # 2. Medical Specializations
        specs_data = [
            {
                'name': 'Cardiology',
                'slug': 'cardiology',
                'icon_name': 'heart-pulse',
                'color_accent': '#EF4444',
                'description': 'Comprehensive cardiovascular care, ECG diagnostics, heart failure management, and preventive heart health.',
                'is_featured': True
            },
            {
                'name': 'Neurology',
                'slug': 'neurology',
                'icon_name': 'brain',
                'color_accent': '#6366F1',
                'description': 'Advanced care for stroke, migraines, epilepsy, neuropathy, and complex central nervous system conditions.',
                'is_featured': True
            },
            {
                'name': 'Pediatrics',
                'slug': 'pediatrics',
                'icon_name': 'baby',
                'color_accent': '#F59E0B',
                'description': 'Compassionate healthcare for infants, children, and adolescents including routine checkups and immunizations.',
                'is_featured': True
            },
            {
                'name': 'Orthopedics',
                'slug': 'orthopedics',
                'icon_name': 'bone',
                'color_accent': '#10B981',
                'description': 'Joint replacement, fracture care, sports medicine, spine health, and musculoskeletal rehabilitation.',
                'is_featured': True
            },
            {
                'name': 'Dermatology',
                'slug': 'dermatology',
                'icon_name': 'sparkles',
                'color_accent': '#EC4899',
                'description': 'Clinical diagnosis and aesthetic care for skin, hair, and nail disorders, acne treatments, and melanoma screening.',
                'is_featured': True
            },
            {
                'name': 'General Medicine',
                'slug': 'general-medicine',
                'icon_name': 'stethoscope',
                'color_accent': '#0284C7',
                'description': 'Primary care, chronic disease management (diabetes, blood pressure), routine physicals, and preventative wellness.',
                'is_featured': True
            },
            {
                'name': 'Ophthalmology',
                'slug': 'ophthalmology',
                'icon_name': 'eye',
                'color_accent': '#06B6D4',
                'description': 'Comprehensive vision exams, cataract surgery, glaucoma therapies, and advanced laser refractive consultations.',
                'is_featured': True
            },
            {
                'name': 'Dentistry',
                'slug': 'dentistry',
                'icon_name': 'smile',
                'color_accent': '#8B5CF6',
                'description': 'Preventative dental hygiene, root canals, cosmetic dentistry, orthodontics, and restorative oral care.',
                'is_featured': True
            },
        ]

        specs_dict = {}
        for s in specs_data:
            spec, _ = Specialization.objects.get_or_create(
                slug=s['slug'],
                defaults=s
            )
            specs_dict[s['name']] = spec
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(specs_dict)} medical specializations."))

        # 3. Doctors
        doctors_info = [
            {
                'username': 'dr_sarah',
                'email': 'sarah.jenkins@medico.com',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'title': 'Dr.',
                'avatar_url': 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&auto=format&fit=crop&q=80',
                'specialization': specs_dict['Cardiology'],
                'qualification': 'MBBS, MD - Cardiology, FACC (Harvard Medical)',
                'experience_years': 14,
                'consultation_fee': 85.00,
                'hospital_name': 'Medico Heart & Vascular Institute',
                'clinic_address': '850 Lexington Ave, Suite 6B, New York, NY',
                'city': 'New York',
                'rating': 4.95,
                'reviews_count': 234,
                'bio': 'Dr. Sarah Jenkins is an internationally recognized cardiologist specializing in preventative cardiovascular therapy, hypertension, and advanced non-invasive cardiac imaging. She has published over 25 papers in prestigious cardiology journals.',
                'consultation_type': 'BOTH',
                'is_verified': True,
                'phone': '+1 (555) 234-8901'
            },
            {
                'username': 'dr_david',
                'email': 'david.chen@medico.com',
                'first_name': 'David',
                'last_name': 'Chen',
                'title': 'Dr.',
                'avatar_url': 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&auto=format&fit=crop&q=80',
                'specialization': specs_dict['Neurology'],
                'qualification': 'MD, PhD in Neurobiology (Johns Hopkins University)',
                'experience_years': 12,
                'consultation_fee': 95.00,
                'hospital_name': 'Medico Brain & Spine Center',
                'clinic_address': '320 E 65th St, New York, NY',
                'city': 'New York',
                'rating': 4.91,
                'reviews_count': 189,
                'bio': 'Dr. David Chen provides clinical neurological diagnosis and treatment for intractable migraines, movement disorders, sleep medicine, and stroke rehabilitation with evidence-based personalized therapy plans.',
                'consultation_type': 'BOTH',
                'is_verified': True,
                'phone': '+1 (555) 345-6789'
            },
            {
                'username': 'dr_emily',
                'email': 'emily.rodriguez@medico.com',
                'first_name': 'Emily',
                'last_name': 'Rodriguez',
                'title': 'Dr.',
                'avatar_url': 'https://images.unsplash.com/photo-1594824813590-77a8fa6a8b23?w=400&auto=format&fit=crop&q=80',
                'specialization': specs_dict['Pediatrics'],
                'qualification': 'MD, FAAP (Stanford Children\'s Health)',
                'experience_years': 9,
                'consultation_fee': 60.00,
                'hospital_name': 'Children\'s Health & Wellness Pavilion',
                'clinic_address': '512 Park Ave S, Suite 400, New York, NY',
                'city': 'New York',
                'rating': 4.98,
                'reviews_count': 310,
                'bio': 'Dr. Emily Rodriguez is a warm, attentive pediatrician passionate about child development, allergy management, nutritional wellness, and providing stress-free experiences for young patients and parents.',
                'consultation_type': 'BOTH',
                'is_verified': True,
                'phone': '+1 (555) 456-7890'
            },
            {
                'username': 'dr_marcus',
                'email': 'marcus.vance@medico.com',
                'first_name': 'Marcus',
                'last_name': 'Vance',
                'title': 'Dr.',
                'avatar_url': 'https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&auto=format&fit=crop&q=80',
                'specialization': specs_dict['Orthopedics'],
                'qualification': 'MD, FAAOS - Orthopedic Surgery (Mayo Clinic)',
                'experience_years': 16,
                'consultation_fee': 110.00,
                'hospital_name': 'Medico Orthopedic & Sports Medicine',
                'clinic_address': '120 W 57th St, 8th Floor, New York, NY',
                'city': 'New York',
                'rating': 4.88,
                'reviews_count': 175,
                'bio': 'Specializing in minimally invasive arthroscopic joint repair, sports injury rehabilitation, knee and shoulder reconstruction. Former team physician for regional collegiate athletic teams.',
                'consultation_type': 'IN_PERSON',
                'is_verified': True,
                'phone': '+1 (555) 567-8901'
            },
            {
                'username': 'dr_olivia',
                'email': 'olivia.taylor@medico.com',
                'first_name': 'Olivia',
                'last_name': 'Taylor',
                'title': 'Dr.',
                'avatar_url': 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=400&auto=format&fit=crop&q=80',
                'specialization': specs_dict['Dermatology'],
                'qualification': 'MD, FAAD - Clinical & Cosmetic Dermatology (Columbia)',
                'experience_years': 10,
                'consultation_fee': 75.00,
                'hospital_name': 'Medico Skin Clinic & Laser Center',
                'clinic_address': '740 Madison Ave, New York, NY',
                'city': 'New York',
                'rating': 4.93,
                'reviews_count': 260,
                'bio': 'Dr. Olivia Taylor focuses on medical dermatology including eczema, psoriasis, acne therapy, mole mapping, and skin cancer prevention using modern dermatological diagnostics.',
                'consultation_type': 'BOTH',
                'is_verified': True,
                'phone': '+1 (555) 678-9012'
            },
            {
                'username': 'dr_james',
                'email': 'james.wilson@medico.com',
                'first_name': 'James',
                'last_name': 'Wilson',
                'title': 'Dr.',
                'avatar_url': 'https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=400&auto=format&fit=crop&q=80',
                'specialization': specs_dict['General Medicine'],
                'qualification': 'MD - Internal Medicine (NYU Grossman School of Medicine)',
                'experience_years': 15,
                'consultation_fee': 55.00,
                'hospital_name': 'Medico Family Care Clinic',
                'clinic_address': '200 Amsterdam Ave, New York, NY',
                'city': 'New York',
                'rating': 4.89,
                'reviews_count': 340,
                'bio': 'Dr. James Wilson provides holistic primary healthcare, routine annual physicals, metabolic syndrome screening, and coordinates multi-disciplinary treatment plans for adult patients.',
                'consultation_type': 'BOTH',
                'is_verified': True,
                'phone': '+1 (555) 789-0123'
            },
        ]

        created_doctors = []
        for d in doctors_info:
            doc_user, u_created = User.objects.get_or_create(
                username=d['username'],
                defaults={
                    'email': d['email'],
                    'first_name': d['first_name'],
                    'last_name': d['last_name'],
                    'role': User.Role.DOCTOR,
                    'phone': d['phone'],
                    'avatar_url': d['avatar_url'],
                }
            )
            if u_created:
                doc_user.set_password('doctor123')
                doc_user.save()

            doc_profile, p_created = DoctorProfile.objects.get_or_create(
                user=doc_user,
                defaults={
                    'title': d['title'],
                    'specialization': d['specialization'],
                    'qualification': d['qualification'],
                    'experience_years': d['experience_years'],
                    'consultation_fee': d['consultation_fee'],
                    'hospital_name': d['hospital_name'],
                    'clinic_address': d['clinic_address'],
                    'city': d['city'],
                    'bio': d['bio'],
                    'rating': d['rating'],
                    'reviews_count': d['reviews_count'],
                    'consultation_type': d['consultation_type'],
                    'is_verified': d['is_verified'],
                    'is_available': True,
                }
            )
            created_doctors.append(doc_profile)

            # Create default schedules: Monday to Friday 09:00 - 17:00, Saturday 10:00 - 14:00
            for day in range(0, 5):
                DoctorSchedule.objects.get_or_create(
                    doctor=doc_profile,
                    day_of_week=day,
                    defaults={
                        'start_time': datetime.time(9, 0),
                        'end_time': datetime.time(17, 0),
                        'slot_duration': 30,
                        'is_active': True,
                    }
                )
            DoctorSchedule.objects.get_or_create(
                doctor=doc_profile,
                day_of_week=5,
                defaults={
                    'start_time': datetime.time(10, 0),
                    'end_time': datetime.time(14, 0),
                    'slot_duration': 30,
                    'is_active': True,
                }
            )

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_doctors)} doctors with active schedules."))

        # 4. Patients
        patients_info = [
            {
                'username': 'john_patient',
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+1 (555) 912-3456',
                'avatar_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80',
                'dob': datetime.date(1990, 5, 14),
                'gender': 'Male',
                'blood_group': 'O+',
                'address': '742 Evergreen Terrace, Brooklyn, NY',
                'city': 'New York',
                'emergency_name': 'Jane Doe (Spouse)',
                'emergency_phone': '+1 (555) 912-3457',
                'allergies': 'Penicillin, Shellfish',
                'chronic_conditions': 'Mild hypertension under regular monitoring'
            },
            {
                'username': 'emma_patient',
                'email': 'emma.watson@example.com',
                'first_name': 'Emma',
                'last_name': 'Watson',
                'phone': '+1 (555) 923-4567',
                'avatar_url': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&auto=format&fit=crop&q=80',
                'dob': datetime.date(1995, 8, 22),
                'gender': 'Female',
                'blood_group': 'A+',
                'address': '180 Riverside Dr, Apt 4C, New York, NY',
                'city': 'New York',
                'emergency_name': 'Arthur Watson (Father)',
                'emergency_phone': '+1 (555) 923-4568',
                'allergies': 'None known',
                'chronic_conditions': 'Asthma (seasonal)'
            }
        ]

        created_patients = []
        for p in patients_info:
            p_user, u_created = User.objects.get_or_create(
                username=p['username'],
                defaults={
                    'email': p['email'],
                    'first_name': p['first_name'],
                    'last_name': p['last_name'],
                    'role': User.Role.PATIENT,
                    'phone': p['phone'],
                    'avatar_url': p['avatar_url'],
                }
            )
            if u_created:
                p_user.set_password('patient123')
                p_user.save()

            p_profile, _ = PatientProfile.objects.get_or_create(
                user=p_user,
                defaults={
                    'date_of_birth': p['dob'],
                    'gender': p['gender'],
                    'blood_group': p['blood_group'],
                    'address': p['address'],
                    'city': p['city'],
                    'emergency_contact_name': p['emergency_name'],
                    'emergency_contact_phone': p['emergency_phone'],
                    'allergies': p['allergies'],
                    'chronic_conditions': p['chronic_conditions'],
                }
            )
            created_patients.append(p_profile)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(created_patients)} patient accounts."))

        # 5. Appointments & Prescriptions
        today = timezone.localdate()
        tomorrow = today + datetime.timedelta(days=2)
        next_week = today + datetime.timedelta(days=5)
        past_date_1 = today - datetime.timedelta(days=10)
        past_date_2 = today - datetime.timedelta(days=25)

        # Appointment 1: Upcoming Confirmed (John Doe with Dr. Sarah Jenkins)
        appt1, _ = Appointment.objects.get_or_create(
            patient=created_patients[0],
            doctor=created_doctors[0],
            appointment_date=tomorrow,
            appointment_time=datetime.time(10, 30),
            defaults={
                'consultation_type': Appointment.ConsultationType.IN_PERSON,
                'status': Appointment.Status.CONFIRMED,
                'reason_for_visit': 'Routine cardiovascular checkup and ECG review',
                'symptoms': 'Occasional slight palpitations during strenuous morning exercise.',
                'doctor_notes': 'Patient scheduled for standard non-invasive resting ECG.'
            }
        )

        # Appointment 2: Upcoming Pending (Emma Watson with Dr. Emily Rodriguez)
        appt2, _ = Appointment.objects.get_or_create(
            patient=created_patients[1],
            doctor=created_doctors[2],
            appointment_date=next_week,
            appointment_time=datetime.time(14, 0),
            defaults={
                'consultation_type': Appointment.ConsultationType.VIDEO,
                'status': Appointment.Status.CONFIRMED,
                'reason_for_visit': 'Seasonal allergy and respiratory wellness consult',
                'symptoms': 'Mild nocturnal coughing and wheezing with pollen changes.',
                'doctor_notes': 'Video consult link prepared.'
            }
        )

        # Appointment 3: Completed with full Prescription (John Doe with Dr. David Chen)
        appt3, created3 = Appointment.objects.get_or_create(
            patient=created_patients[0],
            doctor=created_doctors[1],
            appointment_date=past_date_1,
            appointment_time=datetime.time(11, 0),
            defaults={
                'consultation_type': Appointment.ConsultationType.IN_PERSON,
                'status': Appointment.Status.COMPLETED,
                'reason_for_visit': 'Frequent tension headaches and sleep disruption',
                'symptoms': 'Bilateral pressing forehead pain occurring 3-4 afternoons per week.',
                'doctor_notes': 'Neurological cranial exam normal. Diagnosis: Stress-induced tension-type headache.'
            }
        )
        if created3 or not hasattr(appt3, 'prescription'):
            medicines_1 = [
                {
                    'name': 'Magnesium Glycinate 400mg',
                    'dosage': '1 tablet',
                    'frequency': 'Once daily at bedtime',
                    'duration': '30 days',
                    'instructions': 'Take with water after dinner'
                },
                {
                    'name': 'Naproxen Sodium 220mg',
                    'dosage': '1 tablet as needed',
                    'frequency': 'Every 8-12 hours for acute pain',
                    'duration': 'As needed (max 3 days)',
                    'instructions': 'Take strictly with meals or milk'
                },
                {
                    'name': 'B-Complex Active Co-enzymes',
                    'dosage': '1 capsule',
                    'frequency': 'Once daily with breakfast',
                    'duration': '60 days',
                    'instructions': 'Enhances nervous system recovery'
                }
            ]
            Prescription.objects.get_or_create(
                appointment=appt3,
                defaults={
                    'patient': created_patients[0],
                    'doctor': created_doctors[1],
                    'diagnosis': 'Stress-Induced Tension-Type Headache with mild insomnia',
                    'medicines': medicines_1,
                    'clinical_notes': 'Cranial nerves II-XII intact. Fundoscopy clear. No signs of secondary etiology. Blood pressure 124/82 mmHg.',
                    'lifestyle_advice': 'Adopt 20-minute screen break rule every 90 minutes. Maintain consistent hydration (min 2.5L water/day). Daily 15-minute gentle neck stretching.',
                    'follow_up_date': today + datetime.timedelta(days=20)
                }
            )

        # Appointment 4: Completed with Prescription (Emma Watson with Dr. Olivia Taylor)
        appt4, created4 = Appointment.objects.get_or_create(
            patient=created_patients[1],
            doctor=created_doctors[4],
            appointment_date=past_date_2,
            appointment_time=datetime.time(15, 30),
            defaults={
                'consultation_type': Appointment.ConsultationType.IN_PERSON,
                'status': Appointment.Status.COMPLETED,
                'reason_for_visit': 'Skin sensitivity, mild rosacea and barrier repair',
                'symptoms': 'Facial redness on cheeks exacerbated by heat and spicy food.',
                'doctor_notes': 'Erythematotelangiectatic rosacea stage 1. Skin barrier impaired.'
            }
        )
        if created4 or not hasattr(appt4, 'prescription'):
            medicines_2 = [
                {
                    'name': 'Azelaic Acid 15% Gel',
                    'dosage': 'Pea-sized amount',
                    'frequency': 'Once daily in the evening',
                    'duration': '60 days',
                    'instructions': 'Apply after gentle hydrating moisturizer'
                },
                {
                    'name': 'Ceramide Intensive Barrier Cream',
                    'dosage': 'Liberal application',
                    'frequency': 'Twice daily (morning and night)',
                    'duration': 'Ongoing',
                    'instructions': 'Gentle patting on damp skin'
                },
                {
                    'name': 'Mineral Broad Spectrum Sunscreen SPF 50+',
                    'dosage': 'Two finger lengths',
                    'frequency': 'Every morning, reapply every 3 hours outside',
                    'duration': 'Daily habitual use',
                    'instructions': 'Non-comedogenic physical zinc oxide filter'
                }
            ]
            Prescription.objects.get_or_create(
                appointment=appt4,
                defaults={
                    'patient': created_patients[1],
                    'doctor': created_doctors[4],
                    'diagnosis': 'Mild Erythematotelangiectatic Rosacea with xerosis',
                    'medicines': medicines_2,
                    'clinical_notes': 'No pustules or ocular involvement noted. Skin barrier compromised due to harsh previous exfoliants.',
                    'lifestyle_advice': 'Strictly avoid hot showers on facial skin. Pause all chemical AHA/BHA peels. Avoid direct sauna exposure.',
                    'follow_up_date': today + datetime.timedelta(days=35)
                }
            )

        # Patient Reviews
        Review.objects.get_or_create(
            doctor=created_doctors[0],
            patient=created_patients[0],
            defaults={
                'rating': 5,
                'comment': 'Dr. Sarah Jenkins is phenomenal! She explained my ECG results thoroughly and put all my anxieties to rest with actionable advice.'
            }
        )
        Review.objects.get_or_create(
            doctor=created_doctors[1],
            patient=created_patients[0],
            defaults={
                'rating': 5,
                'comment': 'Outstanding neurological consultation with Dr. Chen. The tension headache protocol gave me relief within a week!'
            }
        )
        Review.objects.get_or_create(
            doctor=created_doctors[4],
            patient=created_patients[1],
            defaults={
                'rating': 5,
                'comment': 'Dr. Taylor took time to understand my skin sensitivities. The digital prescription and clinic follow-up through Medico was seamless.'
            }
        )

        # 6. Testimonials for Homepage
        testimonials_data = [
            {
                'patient_name': 'Eleanor Vance',
                'patient_location': 'Manhattan, New York',
                'avatar': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&auto=format&fit=crop&q=80',
                'doctor_treated': 'Dr. Sarah Jenkins (Cardiology)',
                'rating': 5,
                'comment': 'Medico transformed how I manage my appointments. Booking Dr. Jenkins took less than 60 seconds, and having my medical history and prescriptions stored in my patient portal is so convenient!',
                'is_featured': True
            },
            {
                'patient_name': 'Michael Sterling',
                'patient_location': 'Brooklyn, New York',
                'avatar': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&auto=format&fit=crop&q=80',
                'doctor_treated': 'Dr. David Chen (Neurology)',
                'rating': 5,
                'comment': 'The transparency in doctor qualifications, real patient reviews, and immediate slot confirmations gives me absolute confidence. Medico is the future of digital healthcare.',
                'is_featured': True
            },
            {
                'patient_name': 'Sophia Martinez',
                'patient_location': 'Queens, New York',
                'avatar': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop&q=80',
                'doctor_treated': 'Dr. Emily Rodriguez (Pediatrics)',
                'rating': 5,
                'comment': 'As a mother of two, finding trusted pediatricians quickly is essential. Dr. Rodriguez was gentle and thorough. The Medico mobile dashboard is clean, fast, and so easy to use.',
                'is_featured': True
            }
        ]
        for t in testimonials_data:
            Testimonial.objects.get_or_create(
                patient_name=t['patient_name'],
                defaults=t
            )

        self.stdout.write(self.style.SUCCESS("Database successfully populated with realistic Medico demo data!"))
        self.stdout.write(self.style.SUCCESS("DEMO ACCOUNTS READY:"))
        self.stdout.write(self.style.NOTICE("  Admin:    admin / adminpassword123"))
        self.stdout.write(self.style.NOTICE("  Doctor:   dr_sarah / doctor123"))
        self.stdout.write(self.style.NOTICE("  Patient:  john_patient / patient123"))
        self.stdout.write(self.style.NOTICE("  Patient:  emma_patient / patient123"))
