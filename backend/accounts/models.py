from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    
    ROLE_CHOICES = [
        (PATIENT, 'Patient'),
        (DOCTOR, 'Doctor'),
    ]
    
    username = None  # ← Username hata diya
    email = models.EmailField(unique=True)  # ← Email se login
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    first_name = models.CharField(max_length=50) # ← naam
    last_name = models.CharField(max_length=50)
    USERNAME_FIELD = 'email'  # ← Email = username
    REQUIRED_FIELDS = []

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    allergies = models.TextField(blank=True)
    chronic_condition = models.CharField(max_length=100, blank=True)

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    hospital = models.CharField(max_length=200, blank=True)
    is_verified = models.BooleanField(default=False)
