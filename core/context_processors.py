from .models import Specialization

def medico_context(request):
    """Context processor providing site-wide data for Medico."""
    specializations_nav = Specialization.objects.all()[:8]
    user = request.user
    role = None
    is_doctor = False
    is_patient = False
    is_admin = False

    if user.is_authenticated:
        role = getattr(user, 'role', None)
        is_doctor = (role == 'DOCTOR')
        is_patient = (role == 'PATIENT')
        is_admin = (role == 'ADMIN' or user.is_superuser or user.is_staff)

    return {
        'specializations_nav': specializations_nav,
        'user_role': role,
        'is_doctor_user': is_doctor,
        'is_patient_user': is_patient,
        'is_admin_user': is_admin,
        'site_name': 'Medico',
        'emergency_phone': '+1 (800) 555-MEDICO',
        'support_email': 'support@medicohealth.com',
    }
