from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PatientProfile, DoctorProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Medico Role & Contact', {'fields': ('role', 'phone', 'avatar_url', 'profile_picture')}),
    )

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'specialization', 'hospital_name', 'consultation_fee', 'is_verified', 'is_available', 'rating')
    list_filter = ('is_verified', 'is_available', 'specialization', 'city')
    search_fields = ('user__first_name', 'user__last_name', 'hospital_name', 'license_number')

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'blood_group', 'city')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'emergency_contact_name')

admin.site.register(User, CustomUserAdmin)
