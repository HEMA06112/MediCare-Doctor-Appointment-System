"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index_page,name='index'),
    path('about',views.about_page,name='about'),
    path('doctor',views.doctor_page,name='doctor'),
    path('profile/<int:id>',views.profile,name='profile'),
    path('department',views.department_page,name='department'),
    path('appointment/<int:id>',views.appointment,name='appointment'),
    path('patient/profile',views.patient_profile,name='patient_profile'),
    path('patient/appointments',views.patient_appointments,name='patient_appointments'),
    path('patient/appointment-history',views.patient_appointment_history,name='patient_appointment_history'),
    path('doctor/my-profile',views.doctor_profile,name='doctor_profile'),
    path('doctor/today-appointments',views.doctor_today_appointments,name='doctor_today_appointments'),
    path('doctor/appointments',views.doctor_appointments,name='doctor_appointments'),
    path('doctor/complete-appointments',views.doctor_pending_appointments,name='doctor_pending_appointments'),
    path('doctor/appointments/<int:id>/complete',views.complete_appointment,name='complete_appointment'),
    path('contact',views.contact_page,name='contact'),
    path('signup',views.signup_page,name='signup'),
    path('login',views.login_page,name='login'),
    path('logout',views.logout_page,name='logout'),

] +static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
