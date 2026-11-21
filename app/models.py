from django.db import models
from django.conf import settings

# Create your models here.
class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='doctor_profile',
    )
    
    name=models.CharField(max_length=100)
    specialization=models.CharField(max_length=100)
    qualification=models.CharField(max_length=100)
    experience=models.IntegerField(help_text="experience in years")
    consultation_fee=models.IntegerField()
    profile_image=models.ImageField(upload_to='doctor')
    available_days=models.CharField(max_length=100)
    available_time=models.CharField(max_length=100)
    bio=models.TextField()
    about=models.TextField()
    is_available=models.BooleanField(default=True)

class Department(models.Model):
    department_name=models.CharField(max_length=100)
    image=models.ImageField(upload_to='department')
    description=models.TextField()

class Patient(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='appointments',
    )
    patient_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    date = models.DateField()
    slot_time = models.TimeField()
    reason = models.TextField()
    completed = models.BooleanField(default=False)

    def _str_(self):
        return self.patient_name

class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone_number=models.CharField(max_length=15)
    subject=models.TextField(max_length=200)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.name
