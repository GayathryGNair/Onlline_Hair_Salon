# myapp/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout as auth_logout
from django.views.decorators.cache import cache_control
from django.core.mail import EmailMessage, send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse

from django.shortcuts import render
from .models import Client
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def gallery(request):
    return render(request, 'gallery.html')

def blog(request):
    return render(request, 'blog.html')

def contact(request):
    return render(request, 'contact.html')

def Book(request):
    return render(request, 'Book.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse
from .models import Client, Employee  # Make sure to import your User subclasses
from django.contrib.auth.hashers import make_password  # For hashing passwords

def forgot_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if the user exists with the provided email
        user = Client.objects.filter(email=email).first() or Employee.objects.filter(email=email).first()
        
        if user:
            # Generate a random token for the password reset
            token = get_random_string(20)
            
            # Build the password reset link
            reset_link = request.build_absolute_uri(reverse('reset_password', args=[token]))
            
            try:
                # Send an email to the user with the reset link
                send_mail(
                    'Password Reset Request',
                    f'Click the link below to reset your password:\n\n{reset_link}',
                    'your-email@example.com',  # Replace with the email address configured in settings.py
                    [email],
                    fail_silently=False,
                )
                
                # Save the reset token to the user's model (assuming the field reset_token exists)
                user.reset_token = token
                user.save()

                # Display success message to the user
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('login')  # Redirect to login after sending the email

            except Exception as e:
                # Display error message if email sending fails
                messages.error(request, f"Error sending email: {str(e)}")
        else:
            # If no user is found with that email
            messages.error(request, 'No account found with that email.')
    
    # Render the forgot password page
    return render(request, 'forgot_reset.html')

def reset_password(request, token):
    # Find the user by the reset token
    user = Client.objects.filter(reset_token=token).first() or Employee.objects.filter(reset_token=token).first()
    
    if user:
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password == confirm_password:
                # Hash the new password before saving it
                user.password = make_password(new_password)  # Use make_password to hash the password
                
                # Clear the reset token after successful reset
                user.reset_token = None
                user.save()

                # Show success message and redirect to login
                messages.success(request, 'Password reset successful. You can now log in.')
                return redirect('login')
            else:
                # Show error if passwords do not match
                messages.error(request, 'Passwords do not match.')
        
        # Render the reset password page if the request method is GET
        return render(request, 'reset_password.html', {'token': token})
    else:
        # If the token is invalid or expired
        messages.error(request, 'Invalid or expired reset token.')
        return redirect('forgot_reset')

def logout(request):
    auth_logout(request)
    request.session.flush()  
    return redirect('login')

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client, Employee  # Make sure to import your models

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        default_admin_email = 'admin@gmail.com'
        default_admin_password = 'admin123'

        # Admin login
        if email == default_admin_email and password == default_admin_password:
            request.session['user_type'] = 'admin'
            messages.success(request, 'Admin login successful!')
            return redirect('admin_dashboard')

        # Try Client login first
        try:
            user = Client.objects.get(email=email)
            if check_password(password, user.password):
                if not user.status:
                    messages.error(request, "Your account is inactive. Please contact admin.")
                    return redirect('login')
                else:
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'client'
                    messages.success(request, 'Login successful!')
                    return redirect('client_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
                return redirect('login')
        except Client.DoesNotExist:
            pass

        # If not a client, try Employee login
        try:
            user = Employee.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['user_type'] = 'employee'
                messages.success(request, 'Login successful!')
                return redirect('employee_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
                return redirect('login')
        except Employee.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

    return render(request, 'login.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from .models import Client, Employee  # Ensure to import your models

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        dob = request.POST['dob']
        contact = request.POST['contact']
        status = request.POST['status']

        # Check if email or contact already exists in both Client and Employee
        if Client.objects.filter(email=email).exists() or Employee.objects.filter(email=email).exists():
            messages.error(request, 'User already exists with this email. Please use a different email.')
            return render(request, 'register.html')  # Re-render the form with error

        if Client.objects.filter(contact=contact).exists() or Employee.objects.filter(contact=contact).exists():
            messages.error(request, 'User already exists with this contact number. Please use a different contact number.')
            return render(request, 'register.html')  # Re-render the form with error

        # Hash the password
        hashed_password = make_password(password)

        # Create user depending on status
        try:
            if status == 'client':
                client = Client(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=hashed_password,  # Store hashed password
                    dob=dob,
                    contact=contact
                )
                client.save()
                messages.success(request, 'Registration successful! You can now log in.')
            elif status == 'employee':
                employee = Employee(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=hashed_password,  # Store hashed password
                    dob=dob,
                    contact=contact
                )
                employee.save()
                messages.success(request, 'Registration successful! You can now log in.')

            # Send confirmation email
            subject = 'Welcome to Our Service'
            message = f'Thank you for registering, {first_name}! Please confirm your email address.'
            from_email = 'glamourquest6@gmail.com'  # Use the same email as configured in settings.py
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            return redirect('login')  # Redirect to login or another page

        except IntegrityError:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, 'register.html')  # Re-render the form with error

    return render(request, 'register.html')  # Render the registration form

def for_men(request):
    return render(request, 'for_men.html')

def for_women(request):
    return render(request, 'for_women.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)

#Client


def client_dashboard(request):
    # Check if user is logged in by verifying the session
    user_id = request.session.get('user_id')

    
    # Fetch the Client object using the user's ID
    try:
        client = Client.objects.get(id=user_id)
    except Client.DoesNotExist:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')  # Redirect if client not found

    context = {
        'client': client,
    }
    return render(request, 'client_dashboard.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def employee_dashboard(request):
     # Check if user is logged in by verifying the session
    user_id = request.session.get('user_id')

    
    # Fetch the Client object using the user's ID
    try:
        employee = Employee.objects.get(id=user_id)
    except Employee.DoesNotExist:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')  # Redirect if client not found

    context = {
        'employee': employee,
    }
    return render(request, 'employee_dashboard.html', context)


def user_profile(request):
    return render(request, 'user_profile.html')

from django.shortcuts import render, redirect
from django.contrib import messages

# def admin_login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
        
#         # Check against predefined credentials
#         if username == 'admin' and password == 'admin123':
#             # Create a custom session for the admin user
#             request.session['is_admin'] = True
#             return redirect('admin_dashboard')  # Redirect to admin dashboard
#         else:
#             messages.error(request, "Invalid username or password. Please try again.")
    
#     return render(request, 'admin_login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')  # Redirect non-admins to login

    # Proceed with loading the admin dashboard
    return render(request, 'admin_dashboard.html')

from django.shortcuts import render
from .models import Client

def manage_client(request):
    # Fetch all clients from the database
    clients = Client.objects.all()  # Fetch all clients
    context = {'clients': clients}  # Passing clients data to the template
    return render(request, 'manage_client.html', context)

def manage_employee(request):
    # Fetch all clients from the database
    employees = Employee.objects.all()  # Fetch all clients
    context = {'employees': employees}  # Passing clients data to the template
    return render(request, 'manage_employee.html', context)


from django.shortcuts import redirect
from django.contrib import messages
from .models import Client

def toggle_client_status(request, client_id):
    if request.method == 'POST':
        client = Client.objects.get(id=client_id)
        client.status = not client.status  # Toggle the status
        client.save()
        messages.success(request, f"Client {client.first_name}'s status updated to {'Active' if client.status else 'Inactive'}.")
    return redirect('manage_client')

from .models import Employee
def toggle_employee_status(request, employee_id):
    if request.method == 'POST':
        employee = Employee.objects.get(id=employee_id)
        employee.status = not employee.status  # Toggle the status
        employee.save()
        messages.success(request, f"employee {employee.first_name}'s status updated to {'Active' if employee.status else 'Inactive'}.")
    return redirect('manage_employee')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client
from .forms import ClientProfileUpdateForm

def client_update(request):
    user_id = request.session.get('user_id')  # Assuming you store the user ID in the session
    client = Client.objects.get(id=user_id)

    if request.method == 'POST':
        form = ClientProfileUpdateForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('client_update')  # Redirect to the client dashboard
    else:
        form = ClientProfileUpdateForm(instance=client)

    return render(request, 'client_update.html', {'form': form})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Client

def client_profile(request):
    # Assuming you store the user ID in the session
    user_id = request.session.get('user_id')
    
    # Fetch the client object based on the stored user ID
    client = Client.objects.get(id=user_id)
    
    # Pass the client object to the template for display
    return render(request, 'client_profile.html', {'client': client})

from django.shortcuts import render, redirect
from django.contrib import messages
  # Make sure to create this form

# def manage_service(request):
#     services = Service.objects.all()

#     if request.method == 'POST':
#         form = ServiceForm(request.POST, request.FILES)  # Use request.FILES for image uploads
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Service added successfully!')
#             return redirect('manage_service')  # Redirect to manage services after adding
#     else:
#         form = ServiceForm()

#     return render(request, 'manage_service.html', {
#         'services': services,
#         'form': form
#     })

def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    messages.success(request, 'Service deleted successfully!')
    return redirect('manage_service')

def edit_services(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('manage_service')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'edit_services.html', {'form': form, 'service': service})

from django.shortcuts import render
from django.contrib import messages
from .models import  Client

def client_services(request):
    # Assuming you store the user ID in the session, or use the request's user object
    user_id = request.session.get('user_id')  # Adjust this if needed based on how you store the session
    client = Client.objects.get(id=user_id)

    # Fetch all services from the database
    services = Service.objects.all()

    # Pass the client and services to the template
    context = {
        'client': client,  # Client data for the profile name and other info
        'services': services,  # Services data to list available services
    }

    return render(request, 'client_services.html', context)


def employee_services(request):
    # Fetch all services from the database
    services = Service.objects.all()

    # Pass the services queryset to the template as a dictionary
    context = {
        'services': services,
    }

    return render(request, 'employee_services.html', context)

from .models import Client

def employee_profile(request):
    # Assuming you store the user ID in the session
    user_id = request.session.get('user_id')
    
    # Fetch the client object based on the stored user ID
    employee = Employee.objects.get(id=user_id)
    
    # Pass the client object to the template for display
    return render(request, 'employee_profile.html', {'employee': employee})

from .forms import EmployeeProfileUpdateForm

def employee_update(request):
    user_id = request.session.get('user_id')  # Assuming you store the user ID in the session
    employee = Employee.objects.get(id=user_id)

    if request.method == 'POST':
        form = EmployeeProfileUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('employee_update')  # Redirect to the employee dashboard
    else:
        form = EmployeeProfileUpdateForm(instance=employee)

    return render(request, 'employee_update.html', {'form': form})

from django.shortcuts import get_object_or_404, redirect
from .models import Employee

# Toggle the active/inactive status
def toggle_employee_status(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.status = not employee.status
    employee.save()
    return redirect('manage_employee')

# Toggle the approval status
def toggle_employee_approval(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.approved = not employee.approved
    employee.save()
    return redirect('manage_employee')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client
from .forms import ClientProfileUpdateForm

def client_update(request):
    user_id = request.session.get('user_id')  # Assuming you store the user ID in the session
    client = Client.objects.get(id=user_id)

    if request.method == 'POST':
        form = ClientProfileUpdateForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('client_dashboard')  # Redirect to the client dashboard
    else:
        form = ClientProfileUpdateForm(instance=client)

    # Pass the client object to the template context
    return render(request, 'client_update.html', {'form': form, 'client': client})

def hair_care_services(request):
    
    # Assuming you store the user ID in the session, or use the request's user object
      return render(request, 'hair_care_services.html')

def hair_cut_services(request):
    return render(request, 'hair_cut_services.html')

def facial_services(request):
    return render(request, 'facial_services.html')

def all_type_skin(request):
    return render(request, 'all_type_skin.html')

def mani_pedi_services(request):
    return render(request, 'mani-pedi-services.html')

def waxing_services(request):
    return render(request, 'waxing-services.html')