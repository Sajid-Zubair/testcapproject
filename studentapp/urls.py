from django.urls import path
from . import views

urlpatterns = [
    path('landing/', views.home, name='landing'),
    path('send_sms/<str:batch>/', views.send_sms_to_all, name='send_sms_to_all'),
     path('input/<str:batch>/', views.input_page, name='input_page'),
    path('student/<str:batch>/', views.students_table, name='students_table'),
]