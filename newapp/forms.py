
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.widgets import DateTimeInput

from .models import User, Appointment, Doctor, Nurse
from django.utils import timezone


User = get_user_model()

# Staff registration form
class StaffRegistrationForm(UserCreationForm):
    DEPARTMENT_CHOICES = (
        ('Doctor', 'Doctor'),
        ('Nurse', 'Nurse'),
    )
    SEX_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='First Name', max_length=100, required=True)
    last_name = forms.CharField(label='Last Name', max_length=100, required=True)
    telephone_number = forms.CharField(label='Telephone Number', max_length=20, required=True)
    address = forms.CharField(label='Address', max_length=255, required=True)
    dob = forms.DateField(widget=DateTimeInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'width: 370px; height: 30px; border-radius: 5px; padding: 10px;'}))
    department = forms.CharField(label='Department', max_length=100, required=True)
    gender = forms.ChoiceField(label='Sex', choices=SEX_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 400px; height: 50px; border-radius: 5px; padding: 10px;'}))
    user_type = forms.ChoiceField(label='Role', choices=DEPARTMENT_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 400px; height: 50px; border-radius: 5px; padding: 10px;'}))
    
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'telephone_number', 'address', 'department', 'dob', 'gender', 'user_type','password1', 'password2')
    
    def save(self, commit=True):
        user = super(StaffRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['email']  # Using email as the username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telephone_number = self.cleaned_data['telephone_number']
        user.address = self.cleaned_data['address']
        user.department = self.cleaned_data['department']
        user.user_type = self.cleaned_data['user_type']
        user.dob = self.cleaned_data['dob']
        user.gender = self.cleaned_data['gender']

        if commit:
            user.save()
        return user
    
    
# Patient registration form
class PatientRegistrationForm(UserCreationForm):
    SEX_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    email = forms.EmailField(label='Email', required=True)
    first_name = forms.CharField(label='First Name', max_length=100, required=True)
    last_name = forms.CharField(label='Last Name', max_length=100, required=True)
    telephone_number = forms.CharField(label='Telephone Number', max_length=20, required=True)
    address = forms.CharField(label='Address', max_length=255, required=True)  
    dob = forms.DateField(widget=DateTimeInput(attrs={'type': 'date'}))  
    gender = forms.ChoiceField(label='Sex', choices=SEX_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 400px; height: 50px; border-radius: 5px; padding: 10px;'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'telephone_number', 'address', 'dob', 'gender', 'password1', 'password2')

    def save(self, commit=True):
        user = super(PatientRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['email']  # Using email as the username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telephone_number = self.cleaned_data['telephone_number']
        user.address = self.cleaned_data['address']
        user.dob = self.cleaned_data['dob']
        user.gender = self.cleaned_data['gender']
        user.user_type = 'Patient'
        if commit:
            user.save()
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'id': 'email'}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control', 'placeholder':'Password', 'id': 'password'}))


class AppointmentForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('', 'Select status'),
        ('NHS', 'NHS'),
        ('Private', 'Private'),
    )
    
    nurse = forms.ModelChoiceField(queryset=Nurse.objects.filter(user__is_approved=True), required=False)
    date = forms.DateField(widget=DateTimeInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=DateTimeInput(attrs={'type': 'time'}))  
    status = forms.ChoiceField(label='Status', choices=STATUS_CHOICES, required=True)
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows":"3"}), required=False)

    class Meta:
        model = Appointment
        fields = ['nurse', 'date', 'start_time', 'status', 'notes']

    def clean(self):
        cleaned_data = super().clean()
        nurse = cleaned_data.get('nurse')
        status = cleaned_data.get('status')
        start_time = cleaned_data.get('start_time')
        date = cleaned_data.get('date')
        current_date = timezone.now().date()

        if not nurse:
            self.add_error('nurse', "Please select a nurse.")

        if not status:
            self.add_error('status', "Please select a status.")
        
        if not date:
            self.add_error('date', "Please select a date.")
        
        elif date < current_date:
            self.add_error('date', "Please select a future date.")
        
        if not start_time:
            self.add_error('start_time', "Please select start time.")
        
        return cleaned_data

class ConsultationForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('', 'Select status'),
        ('NHS', 'NHS'),
        ('Private', 'Private'),
    )
    TYPE_CHOICES = (
        ('', 'Select status'),
        ('consultation', 'consultation'),
        ('surgery', 'surgery'),
    )
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.filter(user__is_approved=True), required=False)
    date = forms.DateField(widget=DateTimeInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=DateTimeInput(attrs={'type': 'time'}))     
    appointment_type = forms.ChoiceField(label='Appointment Type', choices=TYPE_CHOICES, required=True)
    status = forms.ChoiceField(label='Status', choices=STATUS_CHOICES, required=True)
    duration = forms.DurationField(required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows":"3"}), required=False)

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'start_time', 'status', 'appointment_type', 'notes']

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        status = cleaned_data.get('status')
        appointment_type = cleaned_data.get('appointment_type')
        start_time = cleaned_data.get('start_time')
        date = cleaned_data.get('date')

        current_date = timezone.now().date()
        
        if doctor == '':
            raise forms.ValidationError("Please select a doctor.")

        if status == '':
            raise forms.ValidationError("Please select a status.")
        
        if start_time == '':
            raise forms.ValidationError("Please select start time.")
        
        if date < current_date:
            raise forms.ValidationError("Please select a future date.")
        
        if date == '':
            raise forms.ValidationError("Please select a date.")
        
        if appointment_type == '':
            raise forms.ValidationError("Please select appointment type.")
        
        if not doctor:
            self.add_error('nurse', "Please select a nurse.")

        if not status:
            self.add_error('status', "Please select a status.")
        
        if not date:
            self.add_error('date', "Please select a date.")

        elif date < timezone.now().date():
            self.add_error('date', "Please select a future date.")
        
        if not start_time:
            self.add_error('start_time', "Please select start time.")

        if not appointment_type:
            self.add_error('start_time', "Please select an Appointment Type.")

        return cleaned_data
    
class AdminAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'nurse', 'date', 'start_time', 'end_time', 'status', 'appointment_type', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'})
        }
