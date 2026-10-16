# 🏥 MEDICO – Professional Healthcare Management & Appointment Platform

**Medico** is a modern, full-stack healthcare web application engineered with **Python**, **Django 5.1**, **HTML5/CSS3**, and vanilla **JavaScript**. It offers patient appointment scheduling, dual consultation modes (in-person and telemedicine video), doctor practice dashboards, printable digital prescriptions, and an administrative oversight panel.

---

## 🌟 Key Features

### 1. 🎨 Modern Healthcare Design & Aesthetics
- **Curated Medical Palette:** Crisp White, Medical Blue (`#0A66C2`, `#0284C7`), Light Cyan (`#E0F2FE`), and subtle Healing Emerald (`#10B981`).
- **Modern Typography:** Styled with Google Fonts (*Plus Jakarta Sans* and *Inter*).
- **Responsive Layout:** Mobile-first architecture tested across 320px, 360px, 390px, 430px, 768px, 1024px, and 1440px without horizontal overflow.
- **Micro-Interactions & Glassmorphism:** Subtle floating badges, hover lifts, alert notifications, and smooth slot picker transitions.

### 2. 🏠 Homepage Experience
- **Hero Section:** Features headline *"Your Health, Our Priority."*, supporting copy, and prominent CTAs.
- **Integrated Live Search:** Multi-parameter search to filter doctors by name, medical specialty, and consultation mode.
- **Medical Specialties:** 8 clinical disciplines (Cardiology, Neurology, Pediatrics, Orthopedics, Dermatology, General Medicine, Ophthalmology, Dentistry) with customized SVG icons.
- **Featured Specialists:** Real doctor profiles with ratings, experience years, clinic locations, and direct booking triggers.
- **How It Works & Why Choose Medico:** 4-step workflow guide and clinical standards overview.
- **Patient Testimonials & 24/7 Emergency Banner:** Verified reviews and immediate emergency dispatch helpline.

### 3. 👤 Patient Portal & Booking System
- **Registration & Profile:** Track demographics, blood group, emergency contacts, known allergies, and medical conditions.
- **Search & Filters:** Browse physicians by specialty, consultation fee sorting, and city.
- **Real-Time Slot Picker:** Interactive calendar that pulls available 30-minute consultation blocks via AJAX API.
- **Double-Booking Prevention:** Strict server-side validation preventing overlapping bookings for the same doctor and time slot.
- **Appointment Management:** Track upcoming, past, and cancelled visits. Reschedule or cancel upcoming appointments with custom reason tracking.
- **Digital Prescriptions Library:** Access physician clinical diagnosis, medication lists, dosages, and instructions with a printable official medical slip.

### 4. 👨‍⚕️ Doctor Clinical Dashboard
- **Role-Based Distinction:** Separate dashboard with physician workflows.
- **Practice Availability Switch:** 1-click toggle between active booking availability and away mode.
- **Daily Agenda & Queue:** View today's appointments, pending requests, confirmed visits, and completed history.
- **Approval & Consultation Actions:** 1-click appointment approval/rejection.
- **Prescription Generator:** Dynamic prescription writer allowing doctors to add medications, dosages, frequencies, clinical notes, and follow-up dates.
- **Weekly Schedule Overview:** Clinical working hours configuration.

### 5. 🛡️ Administrator Panel
- **System KPIs:** Real-time counters for registered patients, verified doctors, appointments volume, and completed consultations.
- **Doctor Verification Workflow:** 1-click credential auditing to verify or revoke doctor visibility.
- **Appointment Oversight:** System-wide appointment filtering and status inspection.
- **Specialization Management:** Add, edit, or delete medical specialties with icon identifiers and color accents.
- **User Directory:** Audit users, inspect roles, and activate or deactivate accounts.
- **Django Admin Integration:** Access standard Django administration at `/admin/`.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.12+, Django 5.1
- **Database:** SQLite (development, configured cleanly for seamless PostgreSQL deployment)
- **Frontend:** Semantic HTML5, Vanilla CSS3 (Custom Design Tokens, Flexbox, CSS Grid, Fluid Typography), Vanilla JavaScript (AJAX Fetch API)
- **Authentication:** Custom Django User Model (`accounts.User`) with role enumeration (`PATIENT`, `DOCTOR`, `ADMIN`), secure PBKDF2 password hashing, and CSRF protection.

---

## 🚀 Quick Setup & Installation

### 1. Prerequisites
Ensure Python 3.10+ is installed on your machine.

### 2. Navigate to Project
```bash
cd g:/websites/medicos
```

### 3. Install Dependencies
```bash
pip install django pillow
```

### 4. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Populate Realistic Demo Data
Seed the database with verified doctors, medical specializations, patient accounts, realistic appointments, and prescriptions:
```bash
python manage.py populate_db
```

### 6. Run the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🔑 Demo Accounts & Credentials

For fast review and demonstration, the login page (`/accounts/login/`) includes **1-Click Demo Login Buttons** that switch roles instantly:

| Role | Username | Password | Notes |
|---|---|---|---|
| **Administrator** | `admin` | `adminpassword123` | Full access to Admin Panel (`/dashboard/admin-panel/`) and Django Admin (`/admin/`) |
| **Doctor** | `dr_sarah` | `doctor123` | Dr. Sarah Jenkins (Cardiologist) &bull; Doctor Practice Portal |
| **Doctor** | `dr_david` | `doctor123` | Dr. David Chen (Neurologist) &bull; Completed Rx demo |
| **Patient** | `john_patient` | `patient123` | John Doe &bull; Patient Portal with upcoming and past appointments |
| **Patient** | `emma_patient` | `patient123` | Emma Watson &bull; Patient Portal with dermatology Rx |

---

## 🧪 Running Automated Tests

Run the comprehensive test suite verifying registration, doctor search, appointment booking, double-booking prevention, and role-based permissions:

```bash
python manage.py test
```

---

## 📁 Project Architecture

```
medicos/
├── accounts/                  # Custom User model, PatientProfile, DoctorProfile, Auth Views
│   ├── management/commands/   # populate_db seed command
│   ├── forms.py               # Patient & Doctor registration and profile forms
│   ├── models.py              # User, PatientProfile, DoctorProfile models
│   ├── urls.py                # Login, register, profile routes
│   └── views.py               # Auth and profile handlers
├── appointments/              # Core booking engine, prescriptions, reviews
│   ├── models.py              # Appointment, DoctorSchedule, Prescription, Review
│   ├── tests.py               # Automated unit and integration test suite
│   ├── urls.py                # Booking, rescheduling, cancellation, and Rx routes
│   └── views.py               # Slot validation, booking logic, prescription view
├── core/                      # Homepage, specialties, static pages, API
│   ├── context_processors.py  # Site-wide context (specialties nav, emergency hotline)
│   ├── models.py              # Specialization, Testimonial, ContactMessage
│   ├── urls.py                # Public routes and AJAX slots API
│   └── views.py               # Homepage, directory search, slot generator API
├── dashboard/                 # Role-based portals
│   ├── urls.py                # Patient, doctor, and admin dashboard routes
│   └── views.py               # Metrics, verification toggles, Rx creator
├── medico_project/            # Project root settings, WSGI, main URL router
│   ├── settings.py            # Django configuration
│   └── urls.py                # Main URL dispatcher
├── static/
│   ├── css/
│   │   ├── main.css           # Global design system, typography, hero, cards
│   │   └── dashboard.css      # Portal sidebars, metrics, data tables, printable Rx
│   └── js/
│       └── main.js            # Slot picker AJAX, mobile drawer, dynamic Rx items
└── templates/
    ├── base.html              # Responsive header, emergency banner, footer
    ├── accounts/              # Login, patient signup, doctor signup, profile
    ├── appointments/          # Book form, appointment details, reschedule, Rx slip
    ├── core/                  # Home, doctors directory, doctor profile, specialties
    └── dashboard/             # Patient dashboard, doctor dashboard, admin dashboard
```

---

## 📄 License & Compliance Notice
This project is developed for educational and professional demonstration purposes. Realistic demo content is simulated and clearly demarcated.
