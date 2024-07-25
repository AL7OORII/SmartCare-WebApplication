from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from .forms import CustomLoginForm, StaffRegistrationForm, PatientRegistrationForm, AppointmentForm, ConsultationForm, AdminAppointmentForm
# from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Invoice
from django.db.models import Sum
import datetime
import json


from .models import *
from .tasks import notify_admins_about_new_user
from .utils import get_coordinates_from_address, create_event

invalid_access_redirect = """
    <html>
    <head>
        <title>Access Denied</title>
        <script type="text/javascript">
            // Wait for 3 seconds before redirecting
            setTimeout(function() {
                window.location.href = '/'; // Adjust the URL as needed
            }, 3000);
        </script>
    </head>
    <body>
        <p>Access denied. You will be redirected to the home page shortly.</p>
    </body>
    </html>
    """
incorrect_pass_redirect = """
    <html>
    <head>
        <title>Access Denied</title>
        <script type="text/javascript">
            // Wait for 3 seconds before redirecting
            setTimeout(function() {
                window.location.href = '/'; // Adjust the URL as needed
            }, 3000);
        </script>
    </head>
    <body>
        <p>The credentials you entered were incorrect or invalid. You will be redirected to the home page shortly.</p>
    </body>
    </html>
    """
await_apprv_redirect = """
    <html>
    <head>
        <title>Access Denied</title>
        <script type="text/javascript">
            // Wait for 3 seconds before redirecting
            setTimeout(function() {
                window.location.href = '/'; // Adjust the URL as needed
            }, 3000);
        </script>
    </head>
    <body>
        <p>Kindly wait for the admin's approval. You will be redirected to the home page shortly.</p>
    </body>
    </html>
    """
#works great
#add rest of patient details
#implement other users login 
#implement all dashboard functions in this file
success_staff_register_redirect = """
    <html>
    <head>
        <title>Access Denied</title>
        <script type="text/javascript">
            // Wait for 3 seconds before redirecting
            setTimeout(function() {
                window.location.href = '/'; // Adjust the URL as needed
            }, 3000);
        </script>
    </head>
    <body>
        <p>Registration successful, kindly await admin approval. You will be redirected to the Home Page!.</p>
    </body>
    </html>
    """
success_patient_register_redirect = """
    <html>
    <head>
        <title>Patient Login</title>
        <script type="text/javascript">
            // Wait for 3 seconds before redirecting
            setTimeout(function() {
                window.location.href = '/patient/login'; // Adjust the URL as needed
            }, 3000);
        </script>
    </head>
    <body>
        <p>Registration successful. You will be redirected to the Login Page!.</p>
    </body>
    </html>
    """
other_user_access = """
    <html>
    <head>
        <title>Access Denied</title>
        <script type="text/javascript">
            // Wait for 3 seconds before redirecting
            setTimeout(function() {
                window.location.href = '/'; // Adjust the URL as needed
            }, 3000);
        </script>
    </head>
    <body>
        <p>You are logged in as a different user, kindly logout first. You will be redirected to the Home Page.</p>
    </body>
    </html>
    """

def main_page(request):
    return render(request, 'newapp/main_page.html')

def user_logout(request):
    logout(request)
    return render(request, 'newapp/logged_out.html')

#admin_dashboard view
def is_superuser(user):
    return user.is_superuser

def about_us(request):
    return render(request, 'newapp/about_us.html')

def contact_us(request):
    return render(request, 'newapp/contact_us.html')

@user_passes_test(is_superuser)
def admin_dashboard(request):

     # Fetch all doctors and nurses who have not been approved yet
    unapproved_doctors = CustomUser.objects.filter(user_type="Doctor", is_approved=False)
    unapproved_nurses = CustomUser.objects.filter(user_type="Nurse", is_approved=False)
    approved_doctors = CustomUser.objects.filter(user_type="Doctor", is_approved=True)
    approved_nurses = CustomUser.objects.filter(user_type="Nurse", is_approved=True)

    print("Unapproved doctors count:", unapproved_doctors.count())
    print("Unapproved nurses count:", unapproved_nurses.count())

    
    # Fetch all existing users, doctors, nurses, and patients
    all_users = CustomUser.objects.all()
    doctors = CustomUser.objects.filter(user_type="Doctor", is_approved=True)
    nurses = CustomUser.objects.filter(user_type="Doctor", is_approved=True)
    
    # Fetch all patients
    patients = CustomUser.objects.filter(user_type='Patient')
    
    context = {
        'unapproved_doctors': unapproved_doctors,
        'unapproved_nurses': unapproved_nurses,
        'approved_doctors': approved_doctors,
        'approved_nurses': approved_nurses,
        'patients': patients
    }

    return render(request, 'newapp/admin_dashboard.html', context)


def admin_logout(request):
     logout(request)
     return render(request, 'admin/logout.html')

def admin_appointments(request):
    # Fetch all appointments
    appointments = Appointment.objects.all().order_by('-date', 'start_time')

    # Pass appointments to the template
    return render(request, 'newapp/admin_appointments.html', {'appointments': appointments}) 

def admin_invoices(request):
    
    # Fetch all invoices
    invoices = Invoice.objects.all().order_by('-invoice_date')

    # Pass invoices to the template
    return render(request, 'newapp/admin_invoices.html', {'invoices': invoices})

def daily_turnover_report(request):
    today = timezone.now().date()
    turnover = Invoice.objects.filter(invoice_date=today).aggregate(total_turnover=Sum('total_amount'))['total_turnover'] or 0
    return JsonResponse({'turnover': turnover})

def weekly_turnover_report(request):
    today = timezone.now().date()
    start_week = today - datetime.timedelta(days=today.weekday())  # Monday
    end_week = start_week + datetime.timedelta(days=6)  # Sunday
    turnover = Invoice.objects.filter(invoice_date__range=(start_week, end_week)).aggregate(total_turnover=Sum('total_amount'))['total_turnover'] or 0
    return JsonResponse({'turnover': turnover})

def monthly_turnover_report(request):
    today = timezone.now().date()
    start_month = today.replace(day=1)
    end_month = today.replace(day=28) + datetime.timedelta(days=4)  # This ensures we cover the entire month
    end_month = end_month - datetime.timedelta(days=end_month.day)
    turnover = Invoice.objects.filter(invoice_date__range=(start_month, end_month)).aggregate(total_turnover=Sum('total_amount'))['total_turnover'] or 0
    return JsonResponse({'turnover': turnover})

def turnover_report(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    date_format = '%Y-%m-%d'

    try:
        start_date = datetime.datetime.strptime(start_date_str, date_format).date()
        end_date = datetime.datetime.strptime(end_date_str, date_format).date()
        if start_date > end_date:
            return JsonResponse({'error': 'Start date must be before end date.'}, status=400)

        turnover = Invoice.objects.filter(invoice_date__range=(start_date, end_date)).aggregate(total_turnover=Sum('total_amount'))['total_turnover']
        turnover = turnover if turnover is not None else 0
        return JsonResponse({'turnover': turnover})

    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD format.'}, status=400)
    
def admin_add_appointment(request):
    
    return render(request, 'newapp/admin_add_appointment.html') 

@csrf_exempt
def admin_reschedule_appointment(request, appointment_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.date = data['new_date']
            appointment.start_time = data['new_time']
            appointment.save()
            return JsonResponse({'status': 'success'}, safe=False)
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def view_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # Assuming you have a template to display user details
    return render(request, 'user_detail.html', {'user': user})

def delete_user(request, user_id, user_email):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        user.delete()
        # Redirect to a safe page after deletion
        return redirect('admin_dashboard')
    else:
        # Show a confirmation page before deleting
        return render(request, 'confirm_delete.html', {'user_id': user_id}, {'user_email': user_email})
    
@login_required
def delete_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if request.user.is_superuser:  # Ensure only admins can delete
        appointment.delete()
        # stays in the same page
        return redirect('admin_staff_view') 
    else:
        # Handle unauthorized access
        return redirect('login')

@login_required
def admin_add_appointment(request):
    if not request.user.is_superuser:
        return redirect('some_error_page')

    if request.method == 'POST':
        form = AdminAppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment added successfully!")
            return redirect('admin_appointments')  # Redirect to the admin appointments overview page
    else:
        form = AdminAppointmentForm()

    return render(request, 'newapp/admin_add_appointment.html', {'form': form})

@login_required
def admin_cancel_appointment(request, appointment_id):
    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.delete()
        return JsonResponse({'status': 'success', 'message': 'Appointment cancelled successfully'})
    except Appointment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Appointment not found'}, status=404)

def view_patient(request, user_id):
    patient = get_object_or_404(CustomUser, id=user_id)
    
    return render(request, 'newapp/patient_detail.html', {'patient': patient})


def admin_login(request):
    # user = request.user
    # if user.groups.filter(name='Patients').exists():
    #     return redirect('/patient/dashboard')
    # elif user.groups.filter(name='Doctors').exists() or user.groups.filter(name='Nurses').exists():
    #     # In case the authenticated user is not a doctor or nurse
    #     return HttpResponse(js_redirect)
    
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:  # Ensure the user is an admin
                login(request, user)
                return redirect('admin_dashboard')  # Redirect to admin dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'newapp/admin_login.html', {'form': form})


# Views for the custom admin dashboard pages
@login_required
def admin_patient_view(request):
    patients = CustomUser.objects.filter(user_type='Patient').prefetch_related(
        'patient__appointments', 'patient__consultations'
    )
    return render(request, 'newapp/admin_patients.html', {'patients': patients})


@login_required
def admin_staff_view(request):
    # Fetch all staff members (doctors and nurses) with their related data
    staff = CustomUser.objects.filter(user_type__in=['Doctor', 'Nurse']).select_related('doctor', 'nurse')
    return render(request, 'newapp/admin_staff.html', {'staff': staff})



# Patient registration
def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Don't save the User object yet
            user.save()  # Save the User object to the database
            
            # Now that the User object is saved, create the corresponding CustomUser object
            gender = form.cleaned_data['gender']
            dob = form.cleaned_data['dob']
            custom_user = CustomUser.objects.create(
                user=user, 
                user_type='Patient', 
                gender = gender,
                dob = dob
            )
            # Create a Patient object associated with the CustomUser if needed
            Patient.objects.create(user=custom_user)
            
            return HttpResponse(success_patient_register_redirect)
        else:
            # Add an error message
            messages.error(request, f"An error occurred: Please check that you provided the required fields and that your password follows the guideline provided in the form")
    else:
        form = PatientRegistrationForm()
    return render(request, 'newapp/patient_register.html', {'form': form})

# Patient Login
def patient_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return HttpResponse(invalid_access_redirect)
        if request.user.customuser.user_type != 'Patient':
            return HttpResponse(other_user_access)
    
    if request.user.is_authenticated and request.user.customuser.user_type == 'Patient':
        return redirect('/patient/dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.customuser.user_type == 'Patient':
            # session
            login(request, user)
            user_type = request.user.customuser.user_type  
            request.session['user_type'] = user_type
    
            return redirect('/patient/dashboard')
        else:
            return HttpResponse(incorrect_pass_redirect)
        
    return render(request, 'newapp/patient_login.html')

#Patient dashboard access
@login_required
def patient_dashboard(request):
    print(request.session.get("user_type"))
    try:
        custom_user = request.user.customuser  # Access the related CustomUser instance
        patient = Patient.objects.get(user=request.user.customuser.id)
        appointments = Appointment.objects.filter(patient=patient)
        consultations = Consultation.objects.filter(patient=patient)
        if custom_user.user_type == 'Patient':
            return render(
                request, 'newapp/patient_dashboard.html', 
                {
                    "first_name": request.user.first_name.capitalize(),
                    "appointments": appointments,
                    "consultations": consultations,
                    "patient": patient,
                }
            )
        else:
            return HttpResponse(invalid_access_redirect)
    except CustomUser.DoesNotExist or Patient.DoesNotExist:
        return HttpResponse(invalid_access_redirect)
                

# Staff registration
def staff_register(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user.save()

                user_type = form.cleaned_data['user_type']
                gender = form.cleaned_data['gender']
                dob = form.cleaned_data['dob']
                custom_user = CustomUser.objects.create(
                    user=user,
                    dob=dob,
                    gender=gender,
                    user_type=user_type,
                    is_staff=True
                )
                
                # Create either a Doctor or Nurse instance linked to the CustomUser
                if user_type == 'Doctor':
                    Doctor.objects.create(user=custom_user)
                elif user_type == 'Nurse':
                    Nurse.objects.create(user=custom_user)

                # Enqueue the Celery task to notify admins about the new user
                # notify_admins_about_new_user.delay()

                return HttpResponse(success_staff_register_redirect)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, f"form is not valid")
    else:
        form = StaffRegistrationForm()
    return render(request, 'newapp/staff_register.html', {'form': form})

# Staff Login
def staff_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return HttpResponse(invalid_access_redirect)
        if request.user.customuser.user_type == 'Doctor':
            return redirect('/doctor/dashboard')
        elif request.user.customuser.user_type == 'Nurse':
            return redirect('/nurse/dashboard')
        
    if request.user.is_authenticated:
        if request.user.customuser.user_type != 'Doctor' or 'Nurse':
            return HttpResponse(other_user_access)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            custom_user = user.customuser  # Access CustomUser instance associated with the User
            
            if custom_user.user_type == 'Doctor':
                if not custom_user.is_approved:
                    return HttpResponse(await_apprv_redirect)
                # session  
                request.session['user_type'] = custom_user.user_type
                login(request, user)
                return redirect('/doctor/dashboard')
            
            elif custom_user.user_type == 'Nurse':
                if not custom_user.is_approved:
                    return HttpResponse(await_apprv_redirect)
                # session  
                request.session['user_type'] = custom_user.user_type
                login(request, user)
                return redirect('/nurse/dashboard')
            
            else:
                return HttpResponse(incorrect_pass_redirect)
        
        else:
            return HttpResponse(invalid_access_redirect)
    
    return render(request, 'newapp/staff_login.html', {'form': CustomLoginForm()})
                    
# Staff dashboard access       
@login_required
def staff_dashboard(request): 
    try:
        custom_user = request.user.customuser
        if custom_user.user_type == 'Doctor':
            user_instance = CustomUser.objects.get(user=request.user.id)
            doctor = Doctor.objects.get(user=user_instance)
            consultations = Consultation.objects.filter(doctor=doctor, date=datetime.date.today())
            consultations = consultations.order_by('start_time')
            patients = Patient.objects.filter(appointments__doctor=doctor, appointments__date=datetime.date.today())
            return render(request, 'newapp/doctor_dashboard.html', {"user": request.user, "consultations": consultations, "patients": patients})
        elif custom_user.user_type == 'Nurse':
            user_instance = CustomUser.objects.get(user=request.user.id)
            nurse = Nurse.objects.get(user=user_instance)
            appointments = Appointment.objects.filter(nurse=nurse, date=datetime.date.today())
            appointments = appointments.order_by('start_time')
            patients = Patient.objects.filter(appointments__nurse=nurse, appointments__date=datetime.date.today())
            return render(request, 'newapp/nurse_dashboard.html',  {"user": request.user, "appointments": appointments, "patients": patients})
    except CustomUser.DoesNotExist:
        return HttpResponse(invalid_access_redirect)

            
@require_http_methods(["POST"])
def approve_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_approved = True
        user.save()
        return JsonResponse({'status': 'success', 'status_code': 200, 'msg': 'User approved'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'status_code': 401, 'msg': 'User not found'})


@require_http_methods(["POST"])
def reject_user(request, user_id, user_email):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        try:
            user_to_remove = User.objects.get(username=user_email)
            user_to_remove.delete()
        except User.DoesNotExist:
            pass
        return JsonResponse({'status': 'success', 'msg': 'User rejected'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'User not found'})

def edit_user(request, user_id):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=user_id)
            # Update user details based on form data
            # For example:
            # user.user.email = request.POST.get('email')
            # user.user.first_name = request.POST.get('first_name')
            # user.user.last_name = request.POST.get('last_name')
            # user.user.save()

            return JsonResponse({'status': 'success', 'msg': 'User details updated'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'msg': 'User not found'})
    else:
        return JsonResponse({'status': 'error', 'msg': 'Invalid request method'})

def deactivate_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = False
        user.save()
        return JsonResponse({'status': 'success', 'msg': 'User deactivated'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'User not found'})   

# Handling the business logics 
@login_required
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if not request.POST.get('nurse') == "":
            staff_is_available = check_staff_availability(request.POST.get('nurse'), form["date"].value())

            if not staff_is_available:
                messages.error(request, f"An error occurred: Nurse is not available Today")
                return redirect('patient_dashboard')
        
            if form.is_valid():
                try:
                    patient = Patient.objects.get(user=request.user.customuser.id)
                    appointment_type = "care"
                    appointment = Appointment.objects.create(
                        nurse=form.cleaned_data['nurse'],
                        patient=patient,
                        date=form.cleaned_data['date'],
                        start_time=form.cleaned_data['start_time'],
                        status=form.cleaned_data['status'],
                        appointment_type=appointment_type,
                        notes=form["notes"].value()
                    )
            
                    # Call function to add event to Google Calendar
                    # add_event_to_google_calendar(appointment, request)
                    # create_event()
                    # Redirect to a success URL or another view
                    messages.success(request, f"Appointment with Nurse {appointment.nurse} was successful!")
                    return redirect('patient_dashboard')
                except Exception as e:
                    print(str(e))        
        else:
            messages.error(request, f"An error occurred: Please check that you are booking an appointment a nurse")
            return render(request, 'newapp/create_appointment.html', {'form': form})
    else:
        form = AppointmentForm()
    
    return render(request, 'newapp/create_appointment.html', {'form': form})

@login_required
def make_consultation(request):
    if request.method == 'POST':
        form = ConsultationForm(request.POST)

        if form.is_valid():
            staff_is_available = check_staff_availability(request.POST.get('doctor'), form["date"].value())

            if not staff_is_available:
                messages.error(request, f"An error occurred: Staff is not available Today")
                return render(request, 'newapp/create_appointment.html', {'form': form})

            try:
                patient = Patient.objects.get(user=request.user.customuser.id)
                consultation = Consultation.objects.create(
                    doctor=form.cleaned_data['doctor'],
                    patient=patient,
                    date=form.cleaned_data['date'],
                    start_time=form.cleaned_data['start_time'],
                    status=form.cleaned_data['status'],
                    appointment_type=form.cleaned_data['appointment_type'],
                    notes=form["notes"].value()
                )
        
                # Call function to add event to Google Calendar
                # add_event_to_google_calendar(appointment, request)
                # create_event()
                # Redirect to a success URL or another view
                
                messages.success(request, f"Consultation with Doctor {consultation.doctor} was successful!")
                return redirect('patient_dashboard')
            except Exception as e:
                print(str(e)) 
        else:
            print("Form not valid")       
    else:
        form = ConsultationForm()
    
    return render(request, 'newapp/create_appointment.html', {'form': form})

@login_required
def make_prescription(request, consultation_id):
    if request.method == 'POST':
        # Extract prescription data from request
        form_data = json.loads(request.body)
        # Initialize variables to store description and price
        description = None
        end_time = None
        
        # Iterate through form data and extract values for description and price
        for field in form_data:
            if field['name'] == 'description':
                description = field['value']
            elif field['name'] == 'endTime':
                end_time = field['value']
                end_time = end_time + ":00"
                end_time = datetime.datetime.strptime(end_time, "%H:%M:%S").time()
        # Check if description and price are not None
        if description is not None and end_time is not None:
            consultation = Consultation.objects.get(id=int(consultation_id))
            consultation.end_time = end_time
            consultation.is_prescribed = True
            consultation.save()
            # Create a new Prescription instance
            prescription = Prescription.objects.create(
                consultation_id=consultation_id,
                description=description,
            )
        
            # Return success response
            messages.error(request, 'Prescription submitted successfully.')
            return JsonResponse({'status': 'success', 'message': 'Prescription submitted successfully'})
    else:
        # Return error response if the request method is not POST
        messages.error(request, 'Invalid request method.')
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
def get_prescription_details(request, prescription_id):
    if request.method == 'GET':
        try:
            prescription = Prescription.objects.get(id=prescription_id)
            data = {
                'description': prescription.description,
                
            }
            return JsonResponse({'prescriptionDetails': data})
        except Prescription.DoesNotExist:
            return JsonResponse({'error': 'Prescription not found'}, status=404)
        
@login_required
def reorder_prescription(request, prescription_id):
    try:
        # Get the prescription to be reordered
        original_prescription = Prescription.objects.get(id=prescription_id, consultation__patient__user=request.user.customuser)
        
        # Clone the original prescription to create a new one
        new_prescription = Prescription.objects.create(
            consultation=original_prescription.consultation,
            description=original_prescription.description,
        )
        
        # Respond with success and the ID of the new prescription
        return JsonResponse({
            'status': 'success',
            'message': 'Prescription reordered successfully',
            'new_prescription_id': new_prescription.id
        })

    except Prescription.DoesNotExist:
        # Respond with an error if the prescription does not exist or does not belong to the user
        return JsonResponse({
            'status': 'error',
            'message': 'Prescription not found or not available for reorder.'
        }, status=404)       

@login_required
def patient_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=int(appointment_id))
    return render(request, 'newapp/patient_appointment.html', {"appointment": appointment}) 


@login_required
def patient_consultation(request, consultation_id):
    consultation = Consultation.objects.get(id=int(consultation_id))
    return render(request, 'newapp/patient_appointment.html', {"consultation": consultation}) 

@login_required
def cancel_appointment(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        appointment_id = request.POST.get('appointment_id')
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.delete()
            messages.success(request, 'Appointment canceled successfully.')
            return JsonResponse({'redirect_url': reverse('patient_dashboard')})
        except Appointment.DoesNotExist:
            return JsonResponse({'error': 'Appointment not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400) 
    
@login_required
def cancel_consultation(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        consultation_id = request.POST.get('consultation_id')
        try:
            consultation = Consultation.objects.get(id=consultation_id)
            consultation.delete()
            messages.success(request, 'Consultation canceled successfully.')
            return JsonResponse({'redirect_url': reverse('patient_dashboard')})
        except Appointment.DoesNotExist:
            return JsonResponse({'error': 'Consultation not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400) 
    
def forward_to_specialist(request):
    # Logic to forward the appointment to a specialist
    if request.method == 'POST'and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        appointment_id = request.POST.get('appointment_id')
        end_time = request.POST.get('end_time')
        try:
            appointment = Appointment.objects.get(pk=appointment_id)
            # Update appointment status or perform other actions
            current_time = current_time = datetime.datetime.now().time()
            # Compare the appointment's start time with the current time
            if appointment.start_time > current_time:
                messages.error(request, 'Appointment not started yet.')
                return JsonResponse({'redirect_url': reverse('doctor_dashboard')})
            
            appointment.is_forwarded_to_specialist = True
            appointment.end_time = end_time
            appointment.save()
            messages.success(request, 'Appointment forwarded to specialist.')
            
            if request.user.customuser.user_type == "Doctor":
                return JsonResponse({'redirect_url': reverse('doctor_dashboard')})
            elif request.user.customuser.user_type == "Nurse":
                return JsonResponse({'redirect_url': reverse('nurse_dashboard')})
        except Appointment.DoesNotExist:
            return JsonResponse({'error': 'Appointment not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400) 


def give_care(request):
    # Logic to forward the appointment to a specialist
    if request.method == 'POST'and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        appointment_id = request.POST.get('appointment_id')
        end_time = request.POST.get('end_time') + ":00"
        end_time = datetime.datetime.strptime(end_time, "%H:%M:%S").time()
        try:
            appointment = Appointment.objects.get(pk=appointment_id)
            # Update appointment status or perform other actions
            current_time = current_time = datetime.datetime.now().time()
            # Compare the appointment's start time with the current time
            if appointment.start_time > current_time:
                messages.error(request, 'Appointment not started yet.')
                return JsonResponse({'redirect_url': reverse('nurse_dashboard')})
            
            appointment.is_cared_for = True
            appointment.end_time = end_time
            appointment.save()
            messages.success(request, 'Patient taken care of by you!')
            return JsonResponse({'redirect_url': reverse('nurse_dashboard')})
        except Appointment.DoesNotExist:
            return JsonResponse({'error': 'Appointment not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400) 

@login_required
def generate_invoice(request):
    try:
        user_type = request.user.customuser.user_type
        appointment_id = request.GET.get('appointmentId', '')
        consultation_id = request.GET.get('consultation_id', '')
        today = datetime.date.today()

        if user_type == "Doctor" and consultation_id != '':
            consultation = Consultation.objects.get(id=int(consultation_id))
            patient_status = consultation.status
            total_amount = consultation.consultation_fee
            Invoice.objects.create(
                content_type=ContentType.objects.get_for_model(Consultation),
                object_id=consultation_id,
                total_amount = total_amount,
                patient_status = patient_status,
                invoice_date = today
            )
            consultation.is_generated_invoice = True
            consultation.save()
        elif user_type=="Nurse" and appointment_id != '':
            appointment = Appointment.objects.get(id=int(appointment_id))
            patient_status = appointment.status
            total_amount = appointment.appointment_fee
            invoice = Invoice.objects.create(
                content_type=ContentType.objects.get_for_model(Appointment),
                object_id=appointment_id,
                total_amount = total_amount,
                patient_status = patient_status,
                invoice_date = today
            )
            appointment.is_generated_invoice = True
            appointment.save()
        messages.success(request, "Invoice successfully created!")

        if request.user.customuser.user_type == "Doctor":
            return JsonResponse({'redirect_url': reverse('doctor_dashboard')})
        elif request.user.customuser.user_type == "Nurse":
            return JsonResponse({'redirect_url': reverse('nurse_dashboard')})
    except Exception as e:
        print(str(e))
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    
@login_required
def view_invoice(request):
    try:
        appointment_id = request.GET.get('appointment_id', '')
        consultation_id = request.GET.get('consultation_id', '')

        if consultation_id != '':
            # Get the content type of the appointment model
            content_type = ContentType.objects.get_for_model(Consultation)
            consultation_object_id = int(consultation_id)  
            # Query the Invoice model to check if an invoice exists for the specified appointment
            invoice= Invoice.objects.filter(
                content_type=content_type,
                object_id=consultation_object_id
            )
            invoice = invoice[0]
            invoice = {
                "total_amount": invoice.total_amount,
                "patient_status": invoice.patient_status,
                "payment_status": invoice.payment_status,
                "invoice_date": invoice.invoice_date
            }
            return JsonResponse({'invoice': invoice})
            
        elif appointment_id != '':
            # Get the content type of the appointment model
            content_type = ContentType.objects.get_for_model(Appointment)
            appointment_object_id = int(appointment_id)  
            # Query the Invoice model to check if an invoice exists for the specified appointment
            invoice= Invoice.objects.filter(
                content_type=content_type,
                object_id=appointment_object_id
            )
            invoice = invoice[0]
            invoice = {
                "total_amount": invoice.total_amount,
                "patient_status": invoice.patient_status,
                "payment_status": invoice.payment_status,
                "invoice_date": invoice.invoice_date
            }
            return JsonResponse({'invoice': invoice})
        else:
            return JsonResponse({'error': 'Check that you provided an appointment id or consultation id.'}, status=400)
    except Exception as e:
        print(str(e))
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    

##################################################################
def check_staff_availability(user, date):
    custom_user = CustomUser.objects.get(id=int(user))
    is_available = False
    # Get the current date
    date_object = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    # Get the day of the week as an integer (Monday is 0, Sunday is 6)
    day_of_week_integer = date_object.weekday()
    if custom_user.user_type == "Nurse":
        if day_of_week_integer == 0 or day_of_week_integer == 3:
            is_available = True
    
    if custom_user.user_type == "Doctor":
        doctors = CustomUser.objects.filter(user_type="Doctor")

        position = 0

        for doctor in doctors:
            position += 1
            if doctor==custom_user:
                break

        if position == 1:
            if day_of_week_integer == 4:
                is_available = False
            else:
                is_available = True
        elif position == 2:
            if day_of_week_integer == 0:
                is_available = False
            else:
                is_available = True

    return is_available

























































































































































































































































































































































































































































































































































































































