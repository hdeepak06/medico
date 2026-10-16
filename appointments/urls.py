from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment_general'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<int:pk>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('<int:pk>/prescription/', views.prescription_view, name='prescription_view'),
    path('<int:pk>/review/', views.submit_review, name='submit_review'),
]
