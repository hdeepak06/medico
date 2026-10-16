from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_dispatch, name='dashboard_dispatch'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointment/<int:pk>/<str:action>/', views.doctor_appointment_action, name='doctor_appointment_action'),
    path('doctor/appointment/<int:pk>/complete/', views.doctor_complete_appointment, name='doctor_complete_appointment'),
    path('doctor/toggle-availability/', views.doctor_toggle_availability, name='doctor_toggle_availability'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/verify-doctor/<int:pk>/', views.admin_toggle_doctor_verification, name='admin_toggle_doctor_verification'),
    path('admin-panel/toggle-user/<int:user_id>/', views.admin_toggle_user_active, name='admin_toggle_user_active'),
    path('admin-panel/add-specialty/', views.admin_add_specialization, name='admin_add_specialization'),
    path('admin-panel/delete-specialty/<int:pk>/', views.admin_delete_specialization, name='admin_delete_specialization'),
]
