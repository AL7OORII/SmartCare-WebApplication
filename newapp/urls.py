# app-level urls.py

from django.urls import path
from .views import *
from django.contrib.auth import views as django_views

urlpatterns = [
    path('', main_page, name='main_page'),  # The root URL for the app
    
    #registration pages
    path('patient/register/', patient_register, name='patient_register'),
    path('staff/register/', staff_register, name='staff_register'),
    
    #login pages
    path('custom-admin/login/', admin_login, name='admin_login'),  # URL for admin login view
    path('custom-admin/logout/', admin_logout, name='admin_logout'),
    path('staff/login/', staff_login, name='staff_login'),
    path('patient/login/', patient_login, name='patient_login'),
    
    #redirect logout page
    path('logout/', user_logout, name="logged_out"),
    
    #dashboard pages
    path('patient/dashboard/', patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', staff_dashboard, name='doctor_dashboard'),
    path('nurse/dashboard/', staff_dashboard, name ='nurse_dashboard'),
    path('custom-admin/dashboard/', admin_dashboard, name='admin_dashboard'),  # URL for admin dashboard view

    # New paths for user management actions
    path('cancel-appointment/', cancel_appointment, name='cancel_appointment'),
    path('cancel-consultation/', cancel_consultation, name='cancel_consultation'),
    path('prescriptions/<int:prescription_id>/', get_prescription_details, name='prescription_details'),
    path('reorder-prescription/<int:prescription_id>/', reorder_prescription, name='reorder_prescription'),
    path('generate-invoice/', generate_invoice, name='generate_invoice'),
    path('view-invoice/', view_invoice, name='view_invoice'),
    path('custom-admin/dashboard/approve-user/<int:user_id>/', approve_user, name='approve_user'),
    path('custom-admin/dashboard/reject-user/<int:user_id>/<str:user_email>/', reject_user, name='reject_user'),
    path('edit-user/<int:user_id>/', edit_user, name='edit_user'),
    path('deactivate-user/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('create_appointment/', create_appointment, name='create_appointment'),
    path('give-care/', give_care, name='give_care'),
    path('make_consultation/', make_consultation, name='make_consultation'),
    path('patient/dashboard/appointments/<int:appointment_id>/', patient_appointment, name='patient_appointment'),
    path('patient/dashboard/consultations/<int:consultation_id>/', patient_consultation, name='patient_consultation'),
    path('forward-appointment/', forward_to_specialist, name='forward_to_specialist'),
    path('doctor/dashboard/<int:consultation_id>/', make_prescription, name='make_prescription'),

    #admin customised page
    path('add-doctor-nurse/', staff_register, name='add_doctor_nurse'), # URL for adding a doctor or nurse
    path('add-patient/', patient_register, name='add_patient'),# URL for adding a patient
    path('admin-appointments/', admin_appointments, name='admin_appointments'),# URL for adding an appointment
    path('admin-invoics/', admin_invoices, name='admin_invoices'),# URL for the invoices page
    path('admin-add-appointment/', admin_add_appointment, name='admin_add_appointment'),
    path('patient/<int:user_id>/view/', view_patient, name='view_patient'),
    path('user/<int:user_id>/view/', view_user, name='view_user'),
    path('user/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('custom-admin/turnover-report/', turnover_report, name='custom_admin_turnover_report'),
    path('custom-admin/daily-turnover/', daily_turnover_report, name='daily_turnover'),
    path('custom-admin/weekly-turnover/', weekly_turnover_report, name='weekly_turnover'),
    path('custom-admin/monthly-turnover/', monthly_turnover_report, name='monthly_turnover'),
    path('about-us/', about_us, name='about_us'),
    path('contact-us/', contact_us, name='contact_us'),
    path('custom-admin/patients/', admin_patient_view, name='admin_patient_view'),
    path('custom-admin/staff/', admin_staff_view, name='admin_staff_view'),
    path('custom-admin/delete-appointment/<int:appointment_id>/', delete_appointment, name='delete_appointment'),
    path('admin-cancel-appointment/<int:appointment_id>/', admin_cancel_appointment, name='cancel_admin_appointment'),
    path('admin-add-appointment/', admin_add_appointment, name='admin_add_appointment'),
    path('admin-reschedule-appointment/<int:appointment_id>/', admin_reschedule_appointment, name='admin_reschedule_appointment'),

]
