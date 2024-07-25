from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomLoginForm, StaffRegistrationForm, PatientRegistrationForm
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from .forms import CustomLoginForm 
from django.contrib.auth.decorators import login_required

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
#works great
#add rest of patient details
#implement other users login 
#implement all dashboard functions in this file
# def patient_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')  # Use email as username
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None and user.groups.filter(name='Patients').exists():  # Check for user type
#             login(request, user)
#             return redirect('/patient/dashboard')  # Adjust URL for patient dashboard
#         else:
#             return HttpResponse('Login failed. Please try again.')
    
#     return render(request, 'newapp/patient_login.html', {'form': UserLoginForm()})  # Render empty form initially

# working version
# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             group, created = Group.objects.get_or_create(name='Patients')
#             user.groups.add(group)
#             return redirect('patient/login')
#     else:
#         form  = UserCreationForm()
#     return render(request, 'newapp/register.html', {'form': form})

def main_page(request):
    return render(request, 'newapp/main_page.html')

def user_logout(request):
    logout(request)
    return render(request, 'newapp/logged_out.html')

# def admin_logout(request):
#     logout(request)
#     return render(request, 'admin/logout.html')

#works great
@login_required
def patient_dashboard(request):
    if not request.user.groups.filter(name="Patients").exists():
        return HttpResponse(invalid_access_redirect)
    return render(request, 'newapp/patient_dashboard.html')

#latest testing version
def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='Patients')
            user.groups.add(group)
            return redirect('/patient/login')
    else:
        form  = PatientRegistrationForm()
    return render(request, 'newapp/patient_register.html', {'form': form})

def patient_login(request):
    user = request.user
    if user.groups.filter(name='Patients').exists():
        return redirect('/patient/dashboard')
    elif user.groups.filter(name='Doctors').exists() or user.groups.filter(name='Nurses').exists() or user.is_superuser:
        # In case the authenticated user is not a doctor or nurse
        return HttpResponse(invalid_access_redirect)
    
    elif request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            # The form's clean method now handles authentication and returns the user
            user = form.get_user()
            if user.groups.filter(name='Patients').exists():
                login(request, user)
                return redirect('/patient/dashboard')
            else:
                # In case the user exists but is not a patient
                return HttpResponse(incorrect_pass_redirect)
        else:
            return HttpResponse(incorrect_pass_redirect)
    else:
        form = CustomLoginForm()

    return render(request, 'newapp/patient_login.html', {'form': form})

def admin_login(request):
    # user = request.user
    # if user.groups.filter(name='Patients').exists():
    #     return redirect('/patient/dashboard')
    # elif user.groups.filter(name='Doctors').exists() or user.groups.filter(name='Nurses').exists():
    #     # In case the authenticated user is not a doctor or nurse
    #     return HttpResponse(js_redirect)
    
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['email']  # Use email as username
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:  # Check for staff status
                login(request, user)
                return redirect('admin:index')  # Redirect to Django admin panel
            else:
                # Handle invalid login (e.g., display error message)
                return render(request, 'newapp/admin_login.html', {'form': form})
        else:
            # Handle invalid form (validation errors)
            return render(request, 'newapp/admin_login.html', {'form': form})
    return render(request, 'newapp/admin_login.html', {'form': CustomLoginForm()})  # Render empty form initially


def staff_register(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            if role == 'doctor':
                group = Group.objects.get(name='Doctors')
            if role == 'nurse':
                group = Group.objects.get(name='Nurses')
            
            user.groups.add(group)
            #uncomment once staff login page is split into two
            # if role == 'doctor':
                # return redirect('/doctor/login')
            # if role == 'nurse':
                #return redirect('/nurse/login')
            return redirect('main_page')
                
    else:
        form  = StaffRegistrationForm()
    return render(request, 'newapp/staff_register.html', {'form': form})

def staff_login(request):
    user = request.user
    if user.groups.filter(name='Doctors').exists():
        return redirect('/doctor/dashboard')
    elif user.groups.filter(name='Nurses').exists():
        return redirect('/nurse/dashboard')
        # In case the authenticated user is not a doctor or nurse
    elif user.groups.filter(name='Patients') or user.is_superuser:
      return HttpResponse(invalid_access_redirect)
  
    elif request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
                user = form.get_user()
                if user.groups.filter(name='Doctors').exists():
                    login(request, user)
                    return redirect('/doctor/dashboard')  # Adjust URL for staff dashboard
                elif user.groups.filter(name='Nurses').exists():
                    login(request, user)
                    return redirect('/nurse/dashboard')
                else:
                # Handle invalid login (e.g., display error message)
                    return HttpResponse(incorrect_pass_redirect)
        else:
            # Handle invalid form (validation errors)
            return HttpResponse(invalid_access_redirect)
    else:
        form = CustomLoginForm()
    
    return render(request, 'newapp/staff_login.html', {'form': form})
    
@login_required
def staff_dashboard(request):
    if not request.user.groups.filter(name='Doctors').exists() and not request.user.groups.filter(name='Nurses').exists():
        return HttpResponse("Unauthorized", status=401)
    elif request.user.groups.filter(name='Doctors').exists() and not request.user.groups.filter(name='Nurses').exists():
        return render(request, 'newapp/doctor_dashboard.html')
    elif request.user.groups.filter(name='Nurses').exists() and not request.user.groups.filter(name='Doctors').exists():
        return render(request, 'newapp/nurse_dashboard.html')
    else:
        return HttpResponse(invalid_access_redirect)
    
#what is this for?
def main_page_view(request):
    return render(request, 'newapp/main_page.html')

#what is this for?
def other_page_view(request):
    return render(request,'other_page.html', {'is_main_page': False})
