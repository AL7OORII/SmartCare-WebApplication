from django.contrib.auth.models import User
from django.db import models
from datetime import time
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import datetime

class CustomUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    user_type_choices = (
        ('Admin', 'Admin'),
        ('Patient', 'Patient'),
        ('Doctor', 'Doctor'),
        ('Nurse', 'Nurse'),
    )
    user_type = models.CharField(max_length=20, choices=user_type_choices)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    is_staff = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # New field to track approval status
    
    def __str__(self):
        return f"{self.user.email} - {self.user.first_name} {self.user.last_name}"
    
# Doctor model
class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
 
    def __str__(self):
        return f"{self.user.user.first_name}"
    
# Nurse model
class Nurse(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.user.first_name}"

# Patient model
class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    issues = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.user.first_name} {self.user.user.last_name}: {self.user.user.username}"

#Admin Model
class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.user.first_name} {self.user.last_name}"

# Appointment model
class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments', blank=True, null=True) #changed from first parameter to Doctor instead of staff
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, related_name='appointments', blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True)
    status = models.CharField(max_length=20)
    appointment_type = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    is_cared_for = models.BooleanField(default=False)
    is_generated_invoice = models.BooleanField(default=False)
    appointment_rate = models.DecimalField(max_digits=10, decimal_places=2, default=8.00)
    appointment_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    def duration_in_minutes(self):
        if self.end_time:
            start_datetime = datetime.datetime.combine(datetime.date.today(), self.start_time)
            end_datetime = datetime.datetime.combine(datetime.date.today(), self.end_time)
            duration = end_datetime - start_datetime
            return duration.total_seconds() // 60  # Convert duration to minutes
        else:
            return 0

    def save(self, *args, **kwargs):
        if self.end_time and self.is_cared_for:
            consultation_slots = self.duration_in_minutes() / 10
            self.appointment_fee = consultation_slots * float(self.appointment_rate)  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment: {self.date}:{self.start_time} for {self.patient}"
    

class Consultation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultations', blank=True, null=True) #changed from first parameter to Doctor instead of staff
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True)
    status = models.CharField(max_length=20)
    appointment_type = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    is_forwarded_to_specialist = models.BooleanField(default=False)
    is_prescribed = models.BooleanField(default=False)
    consultation_rate = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    is_generated_invoice = models.BooleanField(default=False)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    def duration_in_minutes(self):
        if self.end_time:
            start_datetime = datetime.datetime.combine(datetime.date.today(), self.start_time)
            end_datetime = datetime.datetime.combine(datetime.date.today(), self.end_time)
            duration = end_datetime - start_datetime
            return duration.total_seconds() // 60  # Convert duration to minutes
        else:
            return 0

    def save(self, *args, **kwargs):
        if self.end_time and (self.is_prescribed or self.is_forwarded_to_specialist):
            consultation_slots = self.duration_in_minutes() / 10
            self.consultation_fee = consultation_slots * float(self.consultation_rate)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Consultation: {self.date}:{self.start_time} for {self.patient}"

# Prescription model
class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    description = models.TextField()

    def __str__(self):
        return f"{self.appointment}"


# Invoice model
class Invoice(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    appointment_or_consultation = GenericForeignKey('content_type', 'object_id')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    patient_status = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=50, default="Not paid")
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
   
    def __str__(self):
        return f"{self.appointment_or_consultation}:{self.total_amount}:{self.patient_status}"

