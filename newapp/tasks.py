# tasks.py
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from django.core.mail import send_mail


User = get_user_model()

@shared_task
def monitor_doctor_registration():
    doctors = User.objects.filter(user_type='doctor', date_joined__gte=timezone.now() - timedelta(minutes=10))
    for doctor in doctors:
        # Perform monitoring or notification tasks here
        print(f"Doctor {doctor.first_name} {doctor.last_name} has been registered.")

        if not doctor.is_staff:
            notify_admins_about_new_user()

@shared_task
def notify_admins_about_new_user():
    try:
        admins = User.objects.filter(is_superuser=True)
        admin_emails = admins.values_list('email', flat=True)
        subject = 'New Staff Registration'
        message = 'A new staff has registered on the platform.'
        send_mail(subject, message, 'onitahcelestine@gmail.com', admin_emails)
    except Exception as e:
        print(str(e))
    subject = 'New Staff Registration'
    message = 'A new staff has registered on the platform.'
    from_email = 'onitahcelestine@gmail.com'
    admins = User.objects.filter(is_superuser=True)
    admin_emails = admins.values_list('email', flat=True)
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, admin_emails)
        except Exception as e:
            print(str(e))