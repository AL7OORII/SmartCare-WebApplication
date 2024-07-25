from django.contrib import admin, messages
from django.utils.translation import ngettext
from django.utils import timezone
from datetime import timedelta

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import *
from .views import approve_user



# Define a custom admin class for your CustomUser model
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name')
    #removed is_staff
    search_fields = ('email', 'name')

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'get_email', 'get_first_name', 'get_last_name', 'user_type', 'is_approved', 'is_staff')  
    search_fields = ('email', 'first_name', 'last_name')  
    list_filter = ('user_type',)  
    actions = ['make_staff']

    def get_email(self, obj):
        return obj.user.email
    
    def get_first_name(self, obj):
        return obj.user.first_name
    
    def get_last_name(self, obj):
        return obj.user.last_name

    get_email.admin_order_field = 'user__email'
    get_first_name.admin_order_field = 'user__first_name'
    get_last_name.admin_order_field = 'user__last_name'
    
    get_email.short_description = 'Email'
    get_first_name.short_description = 'First Name'
    get_last_name.short_description = 'Last Name'

class DoctorAdmin(admin.ModelAdmin):
    actions = ['make_doctor', 'remove_appointment']
    
    @admin.action(description="Mark selected Doctors as approved")
    def make_doctor(self, request, queryset):
        # Count the number of currently approved doctors
        approved_count = Doctor.objects.filter(user__is_approved=True).count()
        
        # Calculate the total number of doctors if we include the selected doctors
        total_count = approved_count + queryset.count()
        
        # Check if the total number of approved doctors won't exceed two after update
        if total_count > 2:
            self.message_user(
                request,
                f"You can't mark more than two doctors as approved.",
                messages.ERROR
            )
            return
        
        # Update the queryset
        updated = 0
        for doctor in queryset:
            if not doctor.user.is_approved:
                doctor.user.is_approved = True
                doctor.user.save()
                updated += 1
        
        self.message_user(
            request,
            ngettext(
                "%d Doctor was successfully marked as approved.",
                "%d Doctors were successfully marked as approved.",
                updated
            ) % updated,
            messages.SUCCESS
        )

    @admin.action(description="Remove second appointment from selected Doctor's schedule")
    # define a custom admin action to remove an appointment
    def remove_appointment(self, request, queryset):
        if queryset.count() == 1:
            user_id = None
            for doctor in queryset:
                user_id = doctor.user.id
            # Filter appointments for Dr. First
            if user_id != None:
                doctor = Doctor.objects.get(user_id=user_id)
                selected_doctor_appointments = Appointment.objects.filter(doctor=doctor)
                # Delete the second appointment from Dr. First's schedule
                if selected_doctor_appointments.count() >= 2:
                    second_appointment = selected_doctor_appointments[1]
                    second_appointment.delete()
                    self.message_user(request, "Second appointment removed from selected Doctor's schedule.")
                else:
                    self.message_user(request, "Selected Doctor does not have a second appointment.", messages.ERROR)
            else:
                self.message_user(request, "Please select a doctor", messages.ERROR)
        else:
            self.message_user(request, "You are not allowed to alter the schedule of the two doctors all at a time", messages.ERROR)

class NurseAdmin(admin.ModelAdmin):

    actions = ['make_nurse']
    
    @admin.action(description="Mark selected Nurse as approved")
    def make_nurse(self, request, queryset):
    
        # Count the number of currently approved doctors
        approved_count = Nurse.objects.filter(user__is_approved=True).count()
        
        # Calculate the total number of doctors if we include the selected doctors
        total_count = approved_count + queryset.count()
        
        # Check if the total number of approved doctors won't exceed two after update
        if total_count > 1:
            self.message_user(
                request,
                f"You can't mark more Nurse as approved.",
                messages.ERROR
            )
            return
        
        # Update the queryset
        updated = 0
        for nurse in queryset:
            if not nurse.user.is_approved:
                nurse.user.is_approved = True
                nurse.user.save()
                updated += 1
        self.message_user(
            request,
            ngettext(
                "%d Nurse was successfully marked as approved.",
                "%d Nurses were successfully marked as approved.",
                updated
            ) % updated,
            messages.SUCCESS
        )
    
class InvoiceAdmin(admin.ModelAdmin):
    # Define a custom admin method to check the turnover of the last month
    actions = ['turnover_last_month']

    @admin.action(description="Check turnover of last month")
    def turnover_last_month(self, request, queryset):
        # Calculate the start and end date of last month
        end_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=1)
        start_date = start_date.replace(day=1)

        # Filter invoices for last month
        last_month_invoices = Invoice.objects.filter(invoice_date__gte=start_date, invoice_date__lte=end_date)
        
        # Calculate total turnover
        total_turnover = sum(invoice.total_amount for invoice in last_month_invoices)

        self.message_user(request, f"Total turnover of last month: {total_turnover}")


class PatientAdmin(admin.ModelAdmin):
    list_filter = ()

# Register your models with their respective admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Nurse, NurseAdmin)
admin.site.register(Admin)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(Invoice, InvoiceAdmin)