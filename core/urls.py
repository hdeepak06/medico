from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('specialties/', views.specialty_list, name='specialty_list'),
    path('specialties/<slug:slug>/', views.specialty_detail, name='specialty_detail'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('api/doctor/<int:doctor_id>/slots/', views.api_doctor_slots, name='api_doctor_slots'),
]
