# myapp/views.py
# index page
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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse
from .models import Client, Employee  # Make sure to import your User subclasses
from django.contrib.auth.hashers import make_password 
from .models import Client, Employee
from django.db import IntegrityError


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

#client
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ClientProfileUpdateForm  # Adjust according to your project structure
from .models import Client
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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

def toggle_client_status(request, client_id):
    if request.method == 'POST':
        client = Client.objects.get(id=client_id)
        client.status = not client.status  # Toggle the status
        client.save()
        messages.success(request, f"Client {client.first_name}'s status updated to {'Active' if client.status else 'Inactive'}.")
    return redirect('manage_client')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def client_update(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')

    client = Client.objects.get(id=user_id)

    if request.method == 'POST':
        form = ClientProfileUpdateForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('client_dashboard')  # Redirect to the client dashboard
    else:
        form = ClientProfileUpdateForm(instance=client)

    return render(request, 'client_update.html', {'form': form, 'client': client})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def client_profile(request):
    # Assuming you store the user ID in the session
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')

    
    # Fetch the client object based on the stored user ID
    client = Client.objects.get(id=user_id)
    
    # Pass the client object to the template for display
    return render(request, 'client_profile.html', {'client': client})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def client_services(request):
    # Assuming you store the user ID in the session, or use the request's user object
    user_id = request.session.get('user_id')  # Adjust this if needed based on how you store the session
    if not user_id:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')
    client = Client.objects.get(id=user_id)

    # Fetch all services from the database
    services = Service.objects.all()

    # Pass the client and services to the template
    context = {
        'client': client,  # Client data for the profile name and other info
        'services': services,  # Services data to list available services
    }

    return render(request, 'client_services.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def hair_care_services(request):
    user_id = request.session.get('user_id')  # Adjust this if needed based on how you store the session
    if not user_id:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')
    client = Client.objects.get(id=user_id)
    
    # Fetch all service subcategories where category ID is 1
    hair_care_subcategories = ServiceSubcategory.objects.filter(category_id=1)
    
    context = {
        'hair_care_subcategories': hair_care_subcategories,
    }
    
    return render(request, 'hair_care_services.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def services_in_subcategory(request, subcategory_id):
    user_id = request.session.get('user_id')  # Adjust this if needed based on how you store the session
    if not user_id:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')
    # Fetch the subcategory and its related services
    subcategory = get_object_or_404(ServiceSubcategory, id=subcategory_id)
    services = Service.objects.filter(subcategory=subcategory)
    
    context = {
        'subcategory': subcategory,
        'services': services,
    }
    
    return render(request, 'services_in_subcategory.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def facial_services(request):
    user_id = request.session.get('user_id')  # Adjust this if needed based on how you store the session
    if not user_id:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')
    facial_service_subcategories = ServiceSubcategory.objects.filter(category_id=2)
    
    context = {
        'facial_service_subcategories': facial_service_subcategories,
    }
    
    return render(request, 'facial_services.html', context)

def hair_cut_services(request):
    return render(request, 'hair_cut_services.html')

def all_type_skin(request):
    return render(request, 'all_type_skin.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def mani_pedi_services(request):
    user_id = request.session.get('user_id')  # Adjust this if needed based on how you store the session
    if not user_id:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')
    
    mani_pedi_service_subcategories = ServiceSubcategory.objects.filter(category_id=3)
    
    context = {
        'mani_pedi_service_subcategories': mani_pedi_service_subcategories,
    }
    
    return render(request, 'mani-pedi-services.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def waxing_services(request):
    user_id = request.session.get('user_id')  # Adjust this if needed based on how you store the session
    if not user_id:
        messages.error(request, "You want to loggin to access dashboard.")
        return redirect('login')
    waxing_service_subcategories = ServiceSubcategory.objects.filter(category_id=4)
    
    context = {
        'waxing_service_subcategories': waxing_service_subcategories,
    }
    
    return render(request, 'waxing-services.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Service

def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'service_detail.html', {'service': service})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Service, Booking
from django.contrib import messages

def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
     # Assuming the client is logged in

    if request.method == 'POST':
        additional_notes = request.POST.get('additional_notes', '')
        booking = Booking.objects.create(
            service=service,
            status='Pending',
            additional_notes=additional_notes
        )
        messages.success(request, 'Booking successful! Your appointment is pending confirmation.')
        return redirect('client_dashboard')

    context = {
        'service': service,
    }
    return render(request, 'book_service.html', context)


# admin 

from django.shortcuts import render
from .models import Client

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')  # Redirect non-admins to login

  
    return render(request, 'admin_dashboard.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_client(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')  
    clients = Client.objects.all()  # Fetch all clients
    context = {'clients': clients}  # Passing clients data to the template
    return render(request, 'manage_client.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_employee(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login') 
    employees = Employee.objects.all()  # Fetch all clients
    context = {'employees': employees}  # Passing clients data to the template
    return render(request, 'manage_employee.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Service, ServiceCategory, ServiceSubcategory
from django.contrib import messages

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_service(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login') 
    if request.method == 'POST':
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        service_name = request.POST.get('service_name')
        description = request.POST.get('description')
        rate = request.POST.get('rate')
        image = request.FILES.get('image')

        # Create a new service
        Service.objects.create(
            subcategory_id=subcategory_id,
            service_name=service_name,
            description=description,
            rate=rate,
            image=image
        )
        messages.success(request, 'Service added successfully.')
        return redirect('manage_service')  # Redirect to the same page

    categories = ServiceCategory.objects.all()
    subcategories = ServiceSubcategory.objects.all()
    services = Service.objects.all()

    return render(request, 'manage_service.html', {
        'categories': categories,
        'subcategories': subcategories,
        'services': services,
        'messages': messages.get_messages(request),
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_services(request, service_id):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        service.subcategory_id = request.POST.get('subcategory')
        service.service_name = request.POST.get('service_name')
        service.description = request.POST.get('description')
        service.rate = request.POST.get('rate')
        if 'image' in request.FILES:
            service.image = request.FILES['image']
        service.save()
        messages.success(request, 'Service updated successfully.')
        return redirect('manage_service')

    categories = ServiceCategory.objects.all()
    subcategories = ServiceSubcategory.objects.all()

    return render(request, 'edit_services.html', {
        'service': service,
        'categories': categories,
        'subcategories': subcategories,
        'messages': messages.get_messages(request),
    })

def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    messages.success(request, 'Service deleted successfully.')
    return redirect('manage_service')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    categories = ServiceCategory.objects.all()
    subcategories = ServiceSubcategory.objects.all()
    services = Service.objects.all()

    if request.method == 'POST':
        if 'category_name' in request.POST:
            # Add Category
            category_name = request.POST['category_name']
            if ServiceCategory.objects.filter(name=category_name).exists():
                messages.error(request, 'Category already exists!')
            else:
                category = ServiceCategory(name=category_name)
                category.save()
                messages.success(request, 'Category added successfully!')
        
        elif 'subcategory_name' in request.POST:
            # Add Subcategory
            subcategory_name = request.POST['subcategory_name']
            category_id = request.POST['category']
            description = request.POST.get('description', '')
            # Check if category exists
            category = get_object_or_404(ServiceCategory, id=category_id)
            if ServiceSubcategory.objects.filter(name=subcategory_name, category=category).exists():
                messages.error(request, 'Subcategory already exists in this category!')
            else:
                # Handle image upload
                subcategory = ServiceSubcategory(
                    name=subcategory_name,
                    category=category,
                    description=description
                )
                
                # Check if an image file was uploaded
                if 'subcategory_image' in request.FILES:
                    subcategory.image = request.FILES['subcategory_image']
                    
                subcategory.save()
                messages.success(request, 'Subcategory added successfully!')
        
        return redirect('category')

    return render(request, 'category.html', {
        'categories': categories,
        'subcategories': subcategories,
        'services': services,
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_category(request, category_id):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    category = get_object_or_404(ServiceCategory, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST['category_name']
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('category')
    
    return render(request, 'edit_category.html', {'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(ServiceCategory, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('category')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_subcategory(request, subcategory_id):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    subcategory = get_object_or_404(ServiceSubcategory, id=subcategory_id)
    
    if request.method == 'POST':
        subcategory_name = request.POST.get('subcategory_name', '').strip()
        category_id = request.POST.get('category', None)
        
        # Validation: Check if subcategory name and category are provided
        if not subcategory_name:
            messages.error(request, 'Subcategory name cannot be empty.')
            return render(request, 'edit_subcategory.html', {
                'subcategory': subcategory,
                'categories': ServiceCategory.objects.all()
            })
        
        if not category_id:
            messages.error(request, 'Please select a valid category.')
            return render(request, 'edit_subcategory.html', {
                'subcategory': subcategory,
                'categories': ServiceCategory.objects.all()
            })

        try:
            # Update the subcategory fields
            subcategory.name = subcategory_name
            subcategory.category_id = category_id
            
            # Handle optional description and image if they are part of the model
            description = request.POST.get('description', '').strip()
            if description:
                subcategory.description = description
            
            if 'subcategory_image' in request.FILES:
                subcategory.image = request.FILES['subcategory_image']
            
            subcategory.save()
            messages.success(request, 'Subcategory updated successfully!')
            return redirect('category')
        except Exception as e:
            messages.error(request, f'Error updating subcategory: {e}')
    
    categories = ServiceCategory.objects.all()
    return render(request, 'edit_subcategory.html', {
        'subcategory': subcategory,
        'categories': categories
    })



def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(ServiceSubcategory, id=subcategory_id)
    subcategory.delete()
    messages.success(request, 'Subcategory deleted successfully!')
    return redirect('category')

#employee

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


def toggle_employee_status(request, employee_id):
    if request.method == 'POST':
        employee = Employee.objects.get(id=employee_id)
        employee.status = not employee.status  # Toggle the status
        employee.save()
        messages.success(request, f"employee {employee.first_name}'s status updated to {'Active' if employee.status else 'Inactive'}.")
    return redirect('manage_employee')


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



