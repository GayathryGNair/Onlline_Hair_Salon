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
from decimal import Decimal
from django.db.models import Q  # Ensure you have this import


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

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect, render
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
                if not user.approved:
                    messages.error(request, "Your account is not yet approved. Please wait for admin approval.")
                    return redirect('login')
                elif not user.status:
                    messages.error(request, "Your account is inactive. Please contact admin.")
                    return redirect('login')
                else:
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
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from .models import Client, Employee  # Ensure you import your models

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        dob = request.POST['dob']
        contact = request.POST['contact']
        gender = request.POST['gender']  # Get the gender from the form

        # Check if email or contact already exists in both Client and Employee
        if Client.objects.filter(email=email).exists() or Employee.objects.filter(email=email).exists():
            messages.error(request, 'User already exists with this email. Please use a different email.')
            return render(request, 'register.html')  # Re-render the form with error

        if Client.objects.filter(contact=contact).exists() or Employee.objects.filter(contact=contact).exists():
            messages.error(request, 'User already exists with this contact number. Please use a different contact number.')
            return render(request, 'register.html')  # Re-render the form with error

        # Hash the password
        hashed_password = make_password(password)

        # Create client
        try:
            client = Client(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=hashed_password,  # Store hashed password
                dob=dob,
                contact=contact,
                gender=gender  # Store the gender
            )
            client.save()
            messages.success(request, 'Registration successful! You can now log in.')

            # Uncomment to send confirmation email
            # subject = 'Welcome to Our Service'
            # message = f'Thank you for registering, {first_name}! Please confirm your email address.'
            # from_email = 'your_email@example.com'  # Use the same email as configured in settings.py
            # recipient_list = [email]
            # send_mail(subject, message, from_email, recipient_list)

            return redirect('login')  # Redirect to login or another page

        except IntegrityError:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, 'client/register.html')  # Re-render the form with error

    return render(request, 'client/register.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Employee, Specialization

def employee_registeration(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        dob = request.POST['dob']
        contact = request.POST['contact']
        qualification_certificate = request.FILES.get('qualification_certificate')
        specialization_ids = request.POST.getlist('specializations')

        if Employee.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'emp/employee_registeration.html', {'specializations': Specialization.objects.all()})

        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
            dob=dob,
            contact=contact,
            qualification_certificate=qualification_certificate
        )
        employee.save()

        # Add specializations
        employee.specializations.set(specialization_ids)

        messages.success(request, 'Registration successful. Please wait for admin approval.')
        return redirect('login')

    specializations = Specialization.objects.all()
    return render(request, 'emp/employee_registeration.html', {'specializations': specializations})

def for_men(request):
    return render(request, 'for_men.html')

def for_women(request):
    return render(request, 'for_women.html')

#client
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def client_dashboard(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')

    if not user_id or user_type != 'client':
        messages.error(request, "You need to log in to access the dashboard.")
        return redirect('login')

    try:
        client = Client.objects.get(id=user_id)
        current_offers = Offer.objects.filter(is_active=True)  # Fetch current active offers
    except Client.DoesNotExist:
        messages.error(request, "Client not found.")
        return redirect('login')

    context = {
        'client': client,
        'current_offers': current_offers,  # Pass current offers to the template
    }
    return render(request, 'client/client_dashboard.html', context)

def toggle_client_status(request, client_id):
    if request.method == 'POST':
        client = Client.objects.get(id=client_id)
        client.status = not client.status  # Toggle the status
        client.save()
        messages.success(request, f"Client {client.first_name}'s status updated to {'Active' if client.status else 'Inactive'}.")
    return redirect('manage_client')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client
from .forms import ClientProfileUpdateForm

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

    return render(request, 'client/client_update.html', {'form': form, 'client': client})

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
    return render(request, 'client/client_profile.html', {'client': client})

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

    return render(request, 'client/client_services.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Service
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'service_detail.html', {'service': service})

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Service, Booking, Employee, Client
from .forms import BookingForm
from django.utils import timezone
from django.core.exceptions import ValidationError

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def booking_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    user_id = request.session.get('user_id')
    client = get_object_or_404(Client, id=user_id)
    
    # Get specialized employees
    specialized_employees = Employee.objects.filter(
        specializations=service.subcategory.category.specialization,
        approved=True,
        status=True
    ).distinct()

    # Fetch the active offer for the service
    active_offer = Offer.objects.filter(
        service=service,
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()

    # Calculate the discounted price if an active offer exists
    if active_offer:
        discount_percentage_decimal = Decimal(active_offer.discount_percentage)
        discounted_price = service.rate - (service.rate * (discount_percentage_decimal / Decimal(100)))
        discount_percentage = active_offer.discount_percentage
    else:
        discounted_price = None
        discount_percentage = None

    # Get existing bookings for today and future
    existing_bookings = Booking.objects.filter(
        service=service,
        booking_date__gte=timezone.now().date(),
        status__in=['Pending', 'Confirmed']
    ).values_list('booking_time', flat=True)

    # Convert time objects to string format before JSON serialization
    existing_booking_times = [booking_time.strftime('%H:%M') for booking_time in existing_bookings]

    if request.method == 'POST':
        form = BookingForm(request.POST, specialized_employees=specialized_employees)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = client
            booking.service = service
            
            try:
                booking.save()
                messages.success(request, "Your booking has been confirmed!")
                return redirect('billing', booking_id=booking.id)
            except Exception as e:
                messages.error(request, f"Error creating booking: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = BookingForm(specialized_employees=specialized_employees)

    # Convert existing bookings to JSON for JavaScript
    existing_booking_json = json.dumps(existing_booking_times)

    context = {
        'service': service,
        'form': form,
        'existing_booking': existing_booking_json,
        'current_time': timezone.now().strftime('%H:%M'),
        'discount_percentage': discount_percentage,
    }

    return render(request, 'client/booking_service.html', context)

# The booking_confirmation view remains unchanged
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def booking_confirmation(request, booking_id):
    user_id = request.session.get('user_id')
    client = get_object_or_404(Client, id=user_id)
    booking = get_object_or_404(Booking, id=booking_id, client=client)
    return render(request, 'client/booking_confirmation.html', {'booking': booking})

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Booking
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def billing(request, booking_id):
    user_id = request.session.get('user_id')
    client = get_object_or_404(Client, id=user_id)
    booking = get_object_or_404(Booking, id=booking_id, client=client)

    # Calculate total cost (if not already calculated)
    
    total_cost = booking.service.rate  # Assuming the service has a rate field
    booking.total_cost = total_cost
    booking.save()

    context = {
        'booking': booking,
        'total_cost': total_cost,
    }
    return render(request, 'client/billing.html', context)

# admin 

from django.shortcuts import render
from .models import Client

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')  # Redirect non-admins to login

  
    return render(request, 'admin/admin_dashboard.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_client(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')  
    clients = Client.objects.all()  # Fetch all clients
    context = {'clients': clients}  # Passing clients data to the template
    return render(request, 'admin/manage_client.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_employee(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login') 
    employees = Employee.objects.all()  # Fetch all clients
    context = {'employees': employees}  # Passing clients data to the template
    return render(request, 'admin/manage_employee.html', context)

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

        # Server-side validation
        if not service_name.isalpha() or not service_name.strip():
            messages.error(request, 'Service name must contain only letters. Please try again.')
            return redirect('manage_service')  # Redirect back to the form

        # Check if the service already exists
        if Service.objects.filter(service_name=service_name).exists():
            messages.error(request, 'A service with this name already exists. Please choose a different name.')
            return redirect('manage_service')  # Redirect back to the form

        if not description.isalpha() or not description.strip():
            messages.error(request, 'Description must contain only letters. Please try again.')
            return redirect('manage_service')  # Redirect back to the form

        try:
            rate_value = int(rate)
            if rate_value <= 0:
                messages.error(request, 'Rate must be a positive integer. Please enter a valid rate.')
                return redirect('manage_service')  # Redirect back to the form
        except (ValueError, TypeError):
            messages.error(request, 'Rate must be a valid positive integer. Please enter a valid rate.')
            return redirect('manage_service')  # Redirect back to the form

        # Create a new service if all validations pass
        Service.objects.create(
            subcategory_id=subcategory_id,
            service_name=service_name,
            description=description,
            rate=rate_value,
            image=image
        )
        messages.success(request, 'Service added successfully.')
        return redirect('manage_service')  # Redirect to the same page

    categories = ServiceCategory.objects.all()
    subcategories = ServiceSubcategory.objects.all()
    services = Service.objects.all()

    return render(request, 'admin/manage_service.html', {
        'categories': categories,
        'subcategories': subcategories,
        'services': services,
        'messages': messages.get_messages(request),  # Pass messages to the template
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

    return render(request, 'admin/edit_services.html', {
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

    return render(request, 'admin/category.html', {
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
        category_name = request.POST['category_name']
        
        # Validation: Check if category name is provided and unique
        if not category_name.isalpha() or not category_name.strip():
            messages.error(request, 'Category name must contain only letters. Please try again.')
            return render(request, 'admin/edit_category.html', {'category': category})  # Re-render with error
        
        if ServiceCategory.objects.filter(name=category_name).exclude(id=category_id).exists():
            messages.error(request, 'Category already exists! Please choose a different name.')
            return render(request, 'admin/edit_category.html', {'category': category})  # Re-render with error

        category.name = category_name
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('category')
    
    return render(request, 'admin/edit_category.html', {'category': category})

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
    
    # Always fetch categories at the start
    categories = ServiceCategory.objects.all()  # Fetch all categories for the dropdown
    
    if request.method == 'POST':
        subcategory_name = request.POST['subcategory_name']
        category_id = request.POST['category']
        description = request.POST['description']
        
        # Validation: Check if subcategory name is provided and unique
        if not subcategory_name.isalpha() or not subcategory_name.strip():
            messages.error(request, 'Subcategory name must contain only letters. Please try again.')
            return render(request, 'admin/edit_subcategory.html', {'subcategory': subcategory, 'categories': categories})  # Re-render with error
        
        # Validation: Check if description contains only letters and spaces
        if not description.isalpha() or not description.strip():
            messages.error(request, 'Description must contain only letters. Please try again.')
            return render(request, 'admin/edit_subcategory.html', {'subcategory': subcategory, 'categories': categories})  # Re-render with error
        

        if ServiceSubcategory.objects.filter(name=subcategory_name).exclude(id=subcategory_id).exists():
            messages.error(request, 'Subcategory already exists! Please choose a different name.')
            return render(request, 'admin/edit_subcategory.html', {'subcategory': subcategory, 'categories': categories})  # Re-render with error

        # Update the subcategory
        subcategory.name = subcategory_name
        subcategory.category_id = category_id
        subcategory.description = description
        
        if 'subcategory_image' in request.FILES:
            subcategory.image = request.FILES['subcategory_image']
        
        subcategory.save()
        messages.success(request, 'Subcategory updated successfully!')
        return redirect('manage_service')  # Redirect to the service management page
    
    return render(request, 'admin/edit_subcategory.html', {'subcategory': subcategory, 'categories': categories})



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
    return render(request, 'emp/employee_dashboard.html', context)

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

    return render(request, 'emp/employee_services.html', context)

from .models import Client
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def employee_profile(request):
    # Assuming you store the user ID in the session
    user_id = request.session.get('user_id')
    
    # Fetch the client object based on the stored user ID
    employee = Employee.objects.get(id=user_id)
    
    # Pass the client object to the template for display
    return render(request, 'emp/employee_profile.html', {'employee': employee})

from .forms import EmployeeProfileUpdateForm

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def employee_update(request):
    user_id = request.session.get('user_id')
    employee = get_object_or_404(Employee, id=user_id)

    if request.method == 'POST':
        # Update employee details
        employee.first_name = request.POST.get('first_name')
        employee.last_name = request.POST.get('last_name')
        employee.email = request.POST.get('email')
        employee.dob = request.POST.get('dob')
        employee.contact = request.POST.get('contact')

        # Handle file upload for qualification certificate
        if request.FILES.get('qualification_certificate'):
            employee.qualification_certificate = request.FILES['qualification_certificate']

        # Save the updated employee object
        employee.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('employee_profile')  # Redirect to the profile page or dashboard

    context = {
        'employee': employee,
    }
    return render(request, 'emp/employee_update.html', context)
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


from django.db.models import Q
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def search_services(request):
    query = request.GET.get('query', '')
    services = Service.objects.filter(
        Q(service_name__icontains=query) |
        Q(description__icontains=query) |
        Q(subcategory__name__icontains=query) |
        Q(subcategory__category__name__icontains=query)
    ).distinct()

    context = {
        'services': services,
        'query': query,
    }
    return render(request, 'client/search_results.html', context)

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from .models import Service, ServiceCategory, ServiceSubcategory, Employee


# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def employee_manage_service(request):
#     user_type = request.session.get('user_type')

#     if user_type != 'employee':
#         messages.error(request, "You need to log in as employee to access this page.")
#         return redirect('login') 

#     if request.method == 'POST':
#         category_id = request.POST.get('category')
#         subcategory_id = request.POST.get('subcategory')
#         service_name = request.POST.get('service_name')
#         description = request.POST.get('description')
#         rate = request.POST.get('rate')
#         image = request.FILES.get('image')

#         Service.objects.create(
#             subcategory_id=subcategory_id,
#             service_name=service_name,
#             description=description,
#             rate=rate,
#             image=image
#         )
#         messages.success(request, 'Service added successfully.')
#         return redirect('employee_manage_service')

#     categories = ServiceCategory.objects.all()
#     subcategories = ServiceSubcategory.objects.all()
#     services = Service.objects.all()

#     return render(request, 'employee_manage_service.html', {
#         'categories': categories,
#         'subcategories': subcategories,
#         'services': services,
#         'messages': messages.get_messages(request),
#     })

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def employee_edit_service(request, service_id):
#     user_type = request.session.get('user_type')

#     if user_type != 'employee':
#         messages.error(request, "You need to log in as employee to access this page.")
#         return redirect('login') 

#     service = get_object_or_404(Service, id=service_id)

#     if request.method == 'POST':
#         service.subcategory_id = request.POST.get('subcategory')
#         service.service_name = request.POST.get('service_name')
#         service.description = request.POST.get('description')
#         service.rate = request.POST.get('rate')
#         if 'image' in request.FILES:
#             service.image = request.FILES['image']
#         service.save()
#         messages.success(request, 'Service updated successfully.')
#         return redirect('employee_manage_service')

#     categories = ServiceCategory.objects.all()
#     subcategories = ServiceSubcategory.objects.all()

#     return render(request, 'employee_edit_service.html', {
#         'service': service,
#         'categories': categories,
#         'subcategories': subcategories,
#     })

# def delete_service(request, service_id):
#     service = get_object_or_404(Service, id=service_id)
#     service.delete()
#     messages.success(request, 'Service deleted successfully.')
#     return redirect('employee_manage_service')


# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def employee_category(request):
#     user_type = request.session.get('user_type')

#     if user_type != 'employee':
#         messages.error(request, "You need to log in as employee to access this page.")
#         return redirect('login') 

#     categories = ServiceCategory.objects.all()
#     subcategories = ServiceSubcategory.objects.all()

#     return render(request, 'employee_category.html', {
#         'categories': categories,
#         'subcategories': subcategories,
#     })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Booking, Employee
from django.utils import timezone
from datetime import date

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_appointments(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')

    if user_type != 'employee':
        messages.error(request, "You need to log in as an employee to access this page.")
        return redirect('login') 

    try:
        employee = Employee.objects.get(id=user_id)
        if not employee.approved:
            messages.error(request, "Your account is not approved yet. Please wait for admin approval.")
            return redirect('employee_dashboard')
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found. Please contact support.")
        return redirect('login')

    # Get appointments for this employee, including today's appointments
    today = date.today()
    appointments = Booking.objects.filter(
        staff=employee,
        booking_date__gte=today
    ).order_by('booking_date', 'booking_time')

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('new_status')
        if booking_id and new_status in ['Confirmed', 'Cancelled', 'Completed']:
            booking = get_object_or_404(Booking, id=booking_id, staff=employee)
            
            # Check if the status change is valid
            if (new_status == 'Confirmed' and booking.status == 'Pending') or \
               (new_status == 'Cancelled' and booking.status in ['Pending', 'Confirmed']) or \
               (new_status == 'Completed' and booking.status == 'Confirmed'):
                booking.status = new_status
                booking.save()
                messages.success(request, f"Appointment status updated to {new_status}")
            else:
                messages.error(request, "Invalid status change.")
            
            return redirect('view_appointments')

    context = {
        'appointments': appointments,
        'employee': employee,
        'today': today
    }
    return render(request, 'emp/view_appointments.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Booking, Feedback
from .forms import FeedbackForm

# ... (existing views)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_feedback(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.booking = booking
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('client_bookings')
    else:
        form = FeedbackForm()
    
    return render(request, 'client/add_feedback.html', {'form': form, 'booking': booking})
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_feedback(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    feedback = get_object_or_404(Feedback, booking=booking)
    return render(request, 'emp/view_feedback.html', {'feedback': feedback})

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Client, Booking

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def client_bookings(request):
    user_id = request.session.get('user_id')
    client = get_object_or_404(Client, id=user_id)
    
    # Get only completed bookings for the client
    completed_bookings = Booking.objects.filter(
        client=client, 
        status='Completed'
    ).order_by('-booking_date', '-booking_time')
    
    # Get today's date for comparison in the template
    today = timezone.now().date()
    
    context = {
        'client': client,
        'bookings': completed_bookings,
        'today': today,
    }
    
    return render(request, 'client/client_bookings.html', context)

# myproject/myapp/views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Client, Booking

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def service_history(request):
    user_id = request.session.get('user_id')
    client = get_object_or_404(Client, id=user_id)
    
    # Get only completed bookings for the client
    completed_bookings = Booking.objects.filter(client=client, status='Completed').order_by('booking_date', 'booking_time')

    context = {
        'client': client,
        'bookings': completed_bookings,
        'today': timezone.now().date(),
    }
    
    return render(request, 'client/service_history.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def employee_bookings(request):
    user_id = request.session.get('user_id')
    employee = get_object_or_404(Employee, id=user_id)
    bookings = Booking.objects.filter(staff=employee).order_by('-booking_date', '-booking_time')
    return render(request, 'emp/employee_bookings.html', {'bookings': bookings})

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Client, Booking

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def client_current_bookings(request):
    user_id = request.session.get('user_id')
    client = get_object_or_404(Client, id=user_id)
    
    # Get only pending and confirmed bookings for the client
    current_bookings = Booking.objects.filter(
        client=client,
        status__in=['Pending', 'Confirmed'],
        booking_date__gte=timezone.now().date()  # Only future and today's bookings
    ).order_by('booking_date', 'booking_time')
    
    context = {
        'client': client,
        'bookings': current_bookings,
        'today': timezone.now().date(),
    }
    
    return render(request, 'client/client_bookings.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Booking, Client

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cancel_booking(request, booking_id):
    # Get the user_id from the session
    user_id = request.session.get('user_id')
    
    # Get the client object or return 404 if not found
    client = get_object_or_404(Client, id=user_id)
    
    # Get the booking object or return 404 if not found
    booking = get_object_or_404(Booking, id=booking_id, client=client)
    
    # Check if the booking can be cancelled
    if booking.status in ['Pending', 'Confirmed'] and booking.booking_date >= timezone.now().date():
        # Update the booking status to 'Cancelled'
        booking.status = 'Cancelled'
        booking.save()
        
        messages.success(request, f"Your booking for {booking.service.service_name} on {booking.booking_date} has been cancelled successfully.")
    else:
        messages.error(request, "This booking cannot be cancelled. It may be in the past or already completed/cancelled.")
    
    # Redirect to the current bookings page
    return redirect('client_dashboard')  # Make sure this URL name exists in your urls.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee, Booking, Feedback  # Assuming you have a Feedback model

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def employee_view_feedback(request):
    user_id = request.session.get('user_id')
    employee = get_object_or_404(Employee, id=user_id)
    
    # Get all completed bookings for this employee that have feedback
    bookings_with_feedback = Booking.objects.filter(
        staff=employee,
        status='Completed',
        feedback__isnull=False
    ).select_related('feedback', 'client', 'service')

    context = {
        'employee': employee,
        'bookings_with_feedback': bookings_with_feedback,
    }
    return render(request, 'emp/employee_view_feedback.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from .models import Booking, Payment, Client, Employee, Service

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def send_bill(request, booking_id):
    # Fetch the booking and related data
    booking = get_object_or_404(Booking, id=booking_id)
    client = booking.client  # Assuming the Booking model has a ForeignKey to Client
    employee = booking.staff  # Assuming the Booking model has a ForeignKey to Employee
    service = booking.service  # Assuming the Booking model has a ForeignKey to Service

    # Set the amount to be billed
    amount = booking.service.rate  # Assuming the rate is the amount to be billed

    # Calculate the discounted price
    if service.discounted_price:  # Check if discounted_price method exists
        discount_amount = amount - service.discounted_price()  # Call the method here
        discounted_price = service.discounted_price()  # Get the discounted price
    else:
        discount_amount = 0  # No discount
        discounted_price = 0  # Set discounted price to 0 if no discount

    if request.method == 'POST':
        # Create a new Payment record
        Payment.objects.create(
            booking=booking,
            client=client,
            employee=employee,
            service=service,
            amount=amount,
            status='Pending',  # Set status to Pending
            # Add payment_id and order_id if applicable
        )
        # Redirect to a success page or back to appointments
        return redirect('view_appointments')  # Change this to your desired redirect

    context = {
        'client': client,
        'employee': employee,
        'service': service,
        'amount': amount,
        'discount_amount': discount_amount,
        'discounted_price': discounted_price,  # Include discounted price in context
        'booking_id': booking_id,
    }
    return render(request, 'emp/sendbill.html', context)


# views.py
# myproject/myapp/views.py
from django.shortcuts import render
from .models import Payment

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_payments(request):
    # Fetch all payments related to the logged-in user (assuming you have a way to identify the user)
    user_id = request.session.get('user_id')  # Example of getting the user ID from the session
    payments = Payment.objects.filter(client__id=user_id)  # Assuming Payment has a ForeignKey to Client

    context = {
        'payments': payments,
    }
    return render(request, 'client/payments.html', context)

# myproject/myapp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Payment

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_payment_status(request, payment_id):
    # Fetch the payment record
    payment = get_object_or_404(Payment, id=payment_id)

    # Update the status to 'Paid'
    if payment.status == 'Pending':
        payment.status = 'Paid'
        payment.save()

    # Redirect back to the payments page
    return redirect('payment')  # Ensure this matches your URL name for payments

# views.py

from .models import Payment, Client, Booking
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def razorpay_payment(request, booking_id):
    user_id = request.session.get('user_id')
    client = get_object_or_404(Client, id=user_id)
    booking = get_object_or_404(Booking, id=booking_id, client=client)

    if request.method == 'POST':
        # Create a Razorpay order
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
        amount = int(booking.service.rate * 100)  # Amount in paise
        currency = 'INR'
        order_data = {
            'amount': amount,
            'currency': currency,
            'payment_capture': '1'  # Auto capture
        }
        order = razorpay_client.order.create(data=order_data)
        return JsonResponse(order)  # Return order details to the frontend

    return render(request, 'client/razorpay_payment.html', {'booking': booking})



from django.shortcuts import render, get_object_or_404, redirect
from .models import Payment, Client, Booking
import razorpay
from django.conf import settings
from django.http import JsonResponse

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pay_now(request, booking_id):
    user_id = request.session.get('user_id')
    client = get_object_or_404(Client, id=user_id)
    booking = get_object_or_404(Booking, id=booking_id, client=client)

    if request.method == 'POST':
        # Get payment details from Razorpay
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')

        # Verify the payment with Razorpay
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
        try:
            # Capture the payment
            response = razorpay_client.payment.capture(razorpay_payment_id, booking.service.rate * 100)  # Amount in paise
            
            # Check if the payment was successful
            if response['status'] == 'captured':
                # Create a new Payment record
                payment = Payment(
                    booking=booking,
                    amount=booking.service.rate,
                    payment_id=razorpay_payment_id,
                    order_id=razorpay_order_id,
                    status='Paid'  # Change status to Paid
                )
                payment.save()  # Save the payment record to the database

                # Update the booking status to 'Paid'
                booking.status = 'Paid'  # Change status from Pending to Paid
                booking.save()  # Save the updated booking

                # Redirect to the payments page
                return redirect('payments')
            else:
                print(f"Payment not captured: {response}")  # Log the response for debugging
                return redirect('payments')  # Redirect back to the payments page on failure
        except Exception as e:
            # Handle the error (e.g., log it, show an error message)
            print(f"Payment failed: {e}")
            return redirect('payments')  # Redirect back to the payments page on failure

    return redirect('payments')  # Redirect if not a POST request

from django.shortcuts import redirect, get_object_or_404
from .models import Payment  # Assuming you have a Payment model

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def confirm_payment(request, transaction_id):
    # Get the payment by ID
    payment = get_object_or_404(Payment, id=transaction_id)  
    payment.status = 'Paid'  # Update the status to 'Paid'
    payment.save()  # Save the changes to the database

    # Redirect to the razorpay_payment view with the booking ID
    return redirect('razorpay_payment', booking_id=payment.booking.id)  # Assuming payment has a booking attribute

def men_services(request):
    return render(request, 'men_services.html')  # Create this template for Men's services

def women_services(request):
    return render(request, 'women_services.html')  # Create this template for Women's services

# myproject/myapp/views.py
# myproject/myapp/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Client, ServiceSubcategory, Service
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def makeup_services(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You need to log in to access the dashboard.")
        return redirect('login')
    
    try:
        client = Client.objects.get(id=user_id)
    except Client.DoesNotExist:
        messages.error(request, "Client profile not found.")
        return redirect('login')
    
    # Fetch all service subcategories where category name is 'Makeup'
    make_up_subcategories = ServiceSubcategory.objects.filter(category__name='Makeup')
    
    # Handle search
    search_query = request.GET.get('query', '')
    if search_query:
        services = Service.objects.filter(
            Q(service_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(subcategory__name__icontains=search_query) |
            Q(subcategory__category__name__icontains=search_query),
            subcategory__category__name='Makeup'  # Ensure we're only searching within makeup services
        ).distinct()
    else:
        services = None
    
    context = {
        'make_up_subcategories': make_up_subcategories,
        'client': client,
        'services': services,
        'query': search_query,
    }
    
    return render(request, 'client/makeup_services.html', context)

# myproject/myapp/views.py

from django.shortcuts import render
from .models import ServiceCategory, ServiceSubcategory, Service  # Import your models

def for_women_services(request):
    # Fetch all categories
    categories = ServiceCategory.objects.all()
    
    # Fetch all subcategories with their related categories
    subcategories = ServiceSubcategory.objects.select_related('category').all()
    
    # Fetch all services with their related subcategories
    services = Service.objects.select_related('subcategory').all()

    # Get the selected category and subcategory IDs from the request
    selected_category_id = request.GET.get('category')
    selected_subcategory_id = request.GET.get('subcategory')

    # Filter subcategories if category is selected
    if selected_category_id:
        subcategories = subcategories.filter(category_id=selected_category_id)
        
    # Filter services if subcategory is selected
    if selected_subcategory_id:
        services = services.filter(subcategory_id=selected_subcategory_id)

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'services': services,
        'selected_category': selected_category_id,
        'selected_subcategory': selected_subcategory_id,
    }

    return render(request, 'forwomen_services.html', context)
##################################################################################
# myproject/myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import ServiceCategoryMen, ServiceSubcategoryMen  # Import your models here
from django.contrib import messages
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_men_category(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')

    categories = ServiceCategoryMen.objects.all()  # Fetch all male categories
    subcategories = ServiceSubcategoryMen.objects.all()  # Fetch all male subcategories

    if request.method == 'POST':
        if 'category_name' in request.POST:
            # Add Category
            category_name = request.POST['category_name']
            if ServiceCategoryMen.objects.filter(name=category_name).exists():
                messages.error(request, 'Category already exists!')
            else:
                category = ServiceCategoryMen(name=category_name)
                category.save()
                messages.success(request, 'Category added successfully!')

        elif 'subcategory_name' in request.POST:
            # Add Subcategory
            subcategory_name = request.POST['subcategory_name']
            category_id = request.POST['category']
            description = request.POST.get('description', '')
            # Check if category exists
            category = get_object_or_404(ServiceCategoryMen, id=category_id)
            if ServiceSubcategoryMen.objects.filter(name=subcategory_name, category=category).exists():
                messages.error(request, 'Subcategory already exists in this category!')
            else:
                # Handle image upload
                subcategory = ServiceSubcategoryMen(
                    name=subcategory_name,
                    category=category,
                    description=description
                )
                
                # Check if an image file was uploaded
                if 'subcategory_image' in request.FILES:
                    subcategory.image = request.FILES['subcategory_image']
                    
                subcategory.save()
                messages.success(request, 'Subcategory added successfully!')

        return redirect('manage_men_category')

    return render(request, 'admin/mens_category.html', {
        'categories': categories,
        'subcategories': subcategories,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ServiceCategoryMen, ServiceSubcategoryMen  # Import your male models
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_men_category(request, category_id):
    
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    
    category = get_object_or_404(ServiceCategoryMen, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST['category_name']
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('manage_men_category')  # Redirect to the men category management page
    
    return render(request, 'admin/edit_men_category.html', {'category': category})

def delete_men_category(request, category_id):
    category = get_object_or_404(ServiceCategoryMen, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('manage_men_category')  # Redirect to the men category management page

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_men_subcategory(request, subcategory_id):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    
    subcategory = get_object_or_404(ServiceSubcategoryMen, id=subcategory_id)
    
    if request.method == 'POST':
        subcategory_name = request.POST.get('subcategory_name', '').strip()
        category_id = request.POST.get('category', None)
        
        # Validation: Check if subcategory name and category are provided
        if not subcategory_name:
            messages.error(request, 'Subcategory name cannot be empty.')
            return render(request, 'admin/edit_men_subcategory.html', {
                'subcategory': subcategory,
                'categories': ServiceCategoryMen.objects.all()
            })
        
        if not category_id:
            messages.error(request, 'Please select a valid category.')
            return render(request, 'admin/edit_men_subcategory.html', {
                'subcategory': subcategory,
                'categories': ServiceCategoryMen.objects.all()
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
            return redirect('manage_men_category')  # Redirect to the men category management page
        except Exception as e:
            messages.error(request, f'Error updating subcategory: {e}')
    
    categories = ServiceCategoryMen.objects.all()
    return render(request, 'admin/edit_men_subcategory.html', {
        'subcategory': subcategory,
        'categories': categories
    })



def delete_men_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(ServiceSubcategoryMen, id=subcategory_id)
    subcategory.delete()
    messages.success(request, 'Subcategory deleted successfully!')
    return redirect('manage_men_category')  # Redirect to the men category management page
# myproject/myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import ServiceMen, ServiceCategoryMen, ServiceSubcategoryMen
from django.contrib import messages
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_men_service(request):
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

        # Server-side validation
        if not service_name.isalpha() or not service_name.strip():
            messages.error(request, 'Service name must contain only letters. Please try again.')
            return redirect('manage_men_service')  # Redirect back to the form

        if not description.isalpha() or not description.strip():
            messages.error(request, 'Description must contain only letters. Please try again.')
            return redirect('manage_men_service')  # Redirect back to the form

        try:
            rate_value = int(rate)
            if rate_value <= 0:
                messages.error(request, 'Rate must be a positive integer. Please enter a valid rate.')
                return redirect('manage_men_service')  # Redirect back to the form
        except (ValueError, TypeError):
            messages.error(request, 'Rate must be a valid positive integer. Please enter a valid rate.')
            return redirect('manage_men_service')  # Redirect back to the form

        # Create a new service if all validations pass
        ServiceMen.objects.create(
            subcategory_id=subcategory_id,
            service_name=service_name,
            description=description,
            rate=rate_value,
            image=image
        )
        messages.success(request, 'Male service added successfully.')
        return redirect('manage_men_service')  # Redirect to the same page

    categories = ServiceCategoryMen.objects.all()
    subcategories = ServiceSubcategoryMen.objects.all()
    services = ServiceMen.objects.all()

    return render(request, 'admin/manage_men_service.html', {
        'categories': categories,
        'subcategories': subcategories,
        'services': services,
        'messages': messages.get_messages(request),  # Pass messages to the template
    })

# myproject/myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import ServiceMen, ServiceCategoryMen, ServiceSubcategoryMen
from django.contrib import messages
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_men_service(request, service_id):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    
    service = get_object_or_404(ServiceMen, id=service_id)

    if request.method == 'POST':
        service.subcategory_id = request.POST.get('subcategory')
        service.service_name = request.POST.get('service_name')
        service.description = request.POST.get('description')
        service.rate = request.POST.get('rate')
        if 'image' in request.FILES:
            service.image = request.FILES['image']
        service.save()
        messages.success(request, 'Service updated successfully.')
        return redirect('manage_men_service')  # Redirect to the male service management page

    categories = ServiceCategoryMen.objects.all()
    subcategories = ServiceSubcategoryMen.objects.all()

    return render(request, 'admin/edit_men_service.html', {
        'service': service,
        'categories': categories,
        'subcategories': subcategories,
        'messages': messages.get_messages(request),
    })

def delete_men_service(request, service_id):
    service = get_object_or_404(ServiceMen, id=service_id)
    service.delete()
    messages.success(request, 'Service deleted successfully.')
    return redirect('manage_men_service')  # Redirect to the male service management page
 
############################################


def dashboard(request):
    return render(request, 'dashboard.html')

from django.shortcuts import render
from .models import ServiceCategory, ServiceSubcategory, Service  # Import existing models

def client_women_services(request):
    # Fetch all categories for women
    categories_women = ServiceCategory.objects.all()
    
    # Fetch all subcategories with their related categories
    subcategories_women = ServiceSubcategory.objects.select_related('category').all()
    
    # Fetch all services with their related subcategories
    services_women = Service.objects.select_related('subcategory').all()

    # Get the selected category and subcategory IDs from the request
    selected_category_id = request.GET.get('category')
    selected_subcategory_id = request.GET.get('subcategory')

    # Filter subcategories if category is selected
    if selected_category_id:
        subcategories_women = subcategories_women.filter(category_id=selected_category_id)
        
    # Filter services if subcategory is selected
    if selected_subcategory_id:
        services_women = services_women.filter(subcategory_id=selected_subcategory_id)

    context = {
        'categories_women': categories_women,
        'subcategories_women': subcategories_women,
        'services_women': services_women,
        'selected_category': selected_category_id,
        'selected_subcategory': selected_subcategory_id,
    }

    # Add debug information to verify data is being passed correctly
    print(f"Number of women's categories: {categories_women.count()}")
    print(f"Number of women's subcategories: {subcategories_women.count()}")
    print(f"Number of women's services: {services_women.count()}")

    return render(request, 'client_women_services.html', context)

from django.shortcuts import render
from .models import ServiceCategoryMen, ServiceSubcategoryMen, ServiceMen  # Import men's models

def client_men_services(request):
    # Fetch all categories for men
    categories_men = ServiceCategoryMen.objects.all()
    
    # Fetch all subcategories with their related categories
    subcategories_men = ServiceSubcategoryMen.objects.select_related('category').all()
    
    # Fetch all services with their related subcategories
    services_men = ServiceMen.objects.select_related('subcategory').all()

    # Get the selected category and subcategory IDs from the request
    selected_category_id = request.GET.get('category')
    selected_subcategory_id = request.GET.get('subcategory')

    # Filter subcategories if category is selected
    if selected_category_id:
        subcategories_men = subcategories_men.filter(category_id=selected_category_id)
        
    # Filter services if subcategory is selected
    if selected_subcategory_id:
        services_men = services_men.filter(subcategory_id=selected_subcategory_id)

    context = {
        'categories_men': categories_men,
        'subcategories_men': subcategories_men,
        'services_men': services_men,
        'selected_category': selected_category_id,
        'selected_subcategory': selected_subcategory_id,
    }

    # Add debug information to verify data is being passed correctly
    print(f"Number of men's categories: {categories_men.count()}")
    print(f"Number of men's subcategories: {subcategories_men.count()}")
    print(f"Number of men's services: {services_men.count()}")

    return render(request, 'client_men_services.html', context)

from django.shortcuts import render
from .models import ServiceCategoryMen, ServiceSubcategoryMen, ServiceMen  # Import men's models

def for_men_services(request):
    # Fetch all categories for men
    categories_men = ServiceCategoryMen.objects.all()
    
    # Fetch all subcategories with their related categories
    subcategories_men = ServiceSubcategoryMen.objects.select_related('category').all()
    
    # Fetch all services with their related subcategories
    services_men = ServiceMen.objects.select_related('subcategory').all()

    # Get the selected category and subcategory IDs from the request
    selected_category_id = request.GET.get('category')
    selected_subcategory_id = request.GET.get('subcategory')

    # Filter subcategories if category is selected
    if selected_category_id:
        subcategories_men = subcategories_men.filter(category_id=selected_category_id)
        
    # Filter services if subcategory is selected
    if selected_subcategory_id:
        services_men = services_men.filter(subcategory_id=selected_subcategory_id)

    context = {
        'categories_men': categories_men,
        'subcategories_men': subcategories_men,
        'services_men': services_men,
        'selected_category': selected_category_id,
        'selected_subcategory': selected_subcategory_id,
    }

    # Add debug information to verify data is being passed correctly
    print(f"Number of men's categories: {categories_men.count()}")
    print(f"Number of men's subcategories: {subcategories_men.count()}")
    print(f"Number of men's services: {services_men.count()}")

    return render(request, 'formen_services.html', context)
############offers##########
from django.shortcuts import render, redirect, get_object_or_404
from .models import Offer, Service
from django.utils import timezone
from django.core.exceptions import ValidationError

def add_offer(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login') 
    selected_category_id = request.POST.get('category') if request.method == 'POST' else None
    selected_subcategory_id = request.POST.get('subcategory') if request.method == 'POST' else None
    selected_service_id = request.POST.get('service') if request.method == 'POST' else None
    services = []

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        discount_percentage = request.POST.get('discount_percentage')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'

        if 'apply_category' in request.POST:
            # Apply offer to all services in the selected category
            services = Service.objects.filter(subcategory__category_id=selected_category_id)
            for service in services:
                try:
                    offer = Offer(
                        service=service,
                        title=title,
                        description=description,
                        discount_percentage=discount_percentage,
                        start_date=start_date,
                        end_date=end_date,
                        is_active=is_active
                    )
                    offer.full_clean()
                    offer.save()
                except ValidationError as e:
                    # Handle validation errors if needed
                    continue
            return redirect('offer_list')

        if 'apply_subcategory' in request.POST:
            # Apply offer to all services in the selected subcategory
            services = Service.objects.filter(subcategory_id=selected_subcategory_id)
            for service in services:
                try:
                    offer = Offer(
                        service=service,
                        title=title,
                        description=description,
                        discount_percentage=discount_percentage,
                        start_date=start_date,
                        end_date=end_date,
                        is_active=is_active
                    )
                    offer.full_clean()
                    offer.save()
                except ValidationError as e:
                    # Handle validation errors if needed
                    continue
            return redirect('admin/offer_list')

        if selected_service_id:
            service = get_object_or_404(Service, id=selected_service_id)
            try:
                offer = Offer(
                    service=service,
                    title=title,
                    description=description,
                    discount_percentage=discount_percentage,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=is_active
                )
                offer.full_clean()
                offer.save()
                return redirect('admin/offer_list')
            except ValidationError as e:
                return render(request, 'admin/add_offer.html', {'errors': e.messages})

    # Fetch categories, subcategories, and services based on selections
    categories = ServiceCategory.objects.all()
    subcategories = ServiceSubcategory.objects.filter(category_id=selected_category_id) if selected_category_id else []
    services = Service.objects.filter(subcategory_id=selected_subcategory_id) if selected_subcategory_id else []

    return render(request, 'admin/add_offer.html', {
        'categories': categories,
        'subcategories': subcategories,
        'services': services,
        'selected_category_id': selected_category_id,
        'selected_subcategory_id': selected_subcategory_id,
        'selected_service_id': selected_service_id,
    })

from django.utils import timezone

def offer_list(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login') 
    # Fetch all offers that are currently active
    current_time = timezone.now()  # Get the current time
    offers = Offer.objects.filter(is_active=True, end_date__gte=current_time)  # Ensure end_date is greater than or equal to current time
    return render(request, 'admin/offer_list.html', {'offers': offers})

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Offer  # Assuming you have an Offer model
from django.views.decorators.csrf import csrf_exempt


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Offer  # Assuming you have an Offer model
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def edit_offer(request, offer_id):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login') 
    offer = get_object_or_404(Offer, id=offer_id)

    if request.method == 'POST':
        offer.title = request.POST.get('title')
        offer.description = request.POST.get('description')
        offer.discount_percentage = request.POST.get('discount_percentage')
        offer.start_date = request.POST.get('start_date')
        offer.end_date = request.POST.get('end_date')
        offer.is_active = request.POST.get('is_active') == 'on'  # Checkbox handling

        # Save the updated offer
        offer.save()
        messages.success(request, 'Offer updated successfully!')
        return redirect('admin/offer_list')  # Redirect to the offer list page

    return render(request, 'admin/edit_offer.html', {'offer': offer})
@csrf_exempt
def delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    if request.method == 'DELETE':
        offer.delete()
        return JsonResponse({'success': True})

from django.shortcuts import render, redirect
from .models import Offer

def delete_all_offers(request):
    if request.method == 'POST':
        Offer.objects.all().delete()  # Delete all offers
        return redirect('admin/offer_list')  # Redirect to the offer list after deletion

from django.db.models import Q
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def search_services_men(request):
    query = request.GET.get('query', '')
    services = ServiceMen.objects.filter(
        Q(service_name__icontains=query) |
        Q(description__icontains=query) |
        Q(subcategory__name__icontains=query) |
        Q(subcategory__category__name__icontains=query)
    ).distinct()

    context = {
        'services': services,
        'query': query,
    }
    return render(request, 'search_results_men.html', context)


####################################################################




#chat bot


import openai
from django.http import JsonResponse
import json
import os



def chatbot_response(request):
    if request.method == 'POST':
        try:
            # Load the user message from the request body
            data = json.loads(request.body)
            user_message = data.get('message', '')

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if you have access
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Extract the response from OpenAI
            bot_response = response['choices'][0]['message']['content']

            return JsonResponse({
                'response': bot_response
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'response': "Sorry, I couldn't process that request. Please try again."
            })
        except Exception as e:
            return JsonResponse({
                'response': f"An error occurred: {str(e)}"
            })

    return JsonResponse({
        'error': 'Invalid request method'
    })



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import google.generativeai as genai
from django.core.files.storage import FileSystemStorage

# Configure logging
logger = logging.getLogger(__name__)

# Set your Gemini API Key
API_KEY = "AIzaSyDeGoQyD0YL2T9nCb33tzOKv0YzzbXStUw"

# Configure the Generative AI client
genai.configure(api_key=API_KEY)

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        try:
            # Load the user message from the request body
            data = json.loads(request.body)
            user_message = data.get('message')

            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            # Create the model
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Generate content using the user message
            response = model.generate_content(user_message)

            # Extract the AI response
            ai_message = response.text

            # Log the AI response for debugging
            logger.info(f"Gemini API response: {ai_message}")

            return JsonResponse({'response': ai_message})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error fetching response from Gemini API: {str(e)}")
            return JsonResponse({'error': 'Failed to get response from AI'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

### image detection ###
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai
from django.core.files.storage import FileSystemStorage

# Configure the Generative AI client
API_KEY = "AIzaSyCIohu_oJ9ayNnrYBKX51vuhsFuLl4VTHY"
genai.configure(api_key=API_KEY)

@csrf_exempt
def analyze_hair_disease(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        
        # Save the uploaded image temporarily
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        file_url = fs.url(filename)

        # Log the image URL for debugging
        logger.info(f"Uploaded image URL: {file_url}")

        # Call the Gemini API to analyze the image
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            # Refine the prompt to focus on identifying specific conditions
            response = model.generate_content(f"Analyze this hair image and provide the specific name of any visible hair problems or conditions (e.g., dandruff, alopecia, etc.): {file_url}")

            # Extract the AI response
            ai_message = response.text.strip()  # Remove any leading/trailing whitespace

            # Log the AI response for debugging
            logger.info(f"AI response: {ai_message}")

            # Return only the name of the problem
            return JsonResponse({'response': ai_message})

        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return JsonResponse({'error': 'Failed to analyze image.'}, status=500)

    return JsonResponse({'error': 'Invalid request method or no image uploaded.'}, status=400)

def upload_hair_image(request):
    return render(request, 'upload_hair_image.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import OfferMale, Service, ServiceCategory, ServiceSubcategory  # Ensure you import your models
from django.utils import timezone

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_offer_male(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')

    categories = ServiceCategoryMen.objects.all()  # Fetch categories for male services
    subcategories = []
    services = []
    selected_category_id = request.POST.get('service_category') if request.method == 'POST' else None
    selected_subcategory_id = request.POST.get('service_subcategory') if request.method == 'POST' else None

    if selected_category_id:
        subcategories = ServiceSubcategoryMen.objects.filter(category_id=selected_category_id)  # Fetch subcategories based on selected category
    if selected_subcategory_id:
        services = ServiceMen.objects.filter(subcategory_id=selected_subcategory_id)

    return render(request, 'admin/add_offer_male.html', {
        'categories': categories,
        'subcategories': subcategories,
        'services': services,
        'selected_category_id': selected_category_id,
        'selected_subcategory_id': selected_subcategory_id,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Offer, Service  # Ensure you import your models

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_offer_male(request, offer_id):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')

    offer = get_object_or_404(Offer, id=offer_id)
    categories = ServiceCategoryMen.objects.all()  # Fetch categories for male services
    subcategories = []
    services = []
    selected_category_id = request.POST.get('service_category', offer.service.subcategory.category.id)  # Default to current offer's category
    selected_subcategory_id = request.POST.get('service_subcategory', offer.service.subcategory.id)  # Default to current offer's subcategory

    if selected_category_id:
        subcategories = ServiceSubcategoryMen.objects.filter(category_id=selected_category_id)  # Fetch subcategories based on selected category
    if selected_subcategory_id:
        services = ServiceMen.objects.filter(subcategory_id=selected_subcategory_id)  # Fetch services based on selected subcategory

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        discount_percentage = request.POST.get('discount_percentage')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'

        # Update the offer
        offer.title = title
        offer.description = description
        offer.discount_percentage = discount_percentage
        offer.start_date = start_date
        offer.end_date = end_date
        offer.is_active = is_active
        offer.save()

        messages.success(request, 'Offer updated successfully!')
        return redirect('admin/offer_list_male')  # Redirect to the offer list page

    return render(request, 'admin/edit_offer_male.html', {
        'offer': offer,
        'categories': categories,
        'subcategories': subcategories,
        'services': services,
        'selected_category_id': selected_category_id,
        'selected_subcategory_id': selected_subcategory_id,
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def offer_list_male(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')

    offers = Offer.objects.all()  # Fetch all offers
    return render(request, 'admin/offer_list_male.html', {
        'offers': offers,
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_offer_male(request, offer_id):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')

    offer = get_object_or_404(Offer, id=offer_id)
    offer.delete()
    messages.success(request, 'Offer deleted successfully!')
    return redirect('offer_list_male')  # Redirect to the offer list page

from django.shortcuts import render
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def service_selection(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    return render(request, 'admin/service_selection.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_selection(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    return render(request, 'admin/category_selection.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def offer_selection(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    return render(request, 'admin/offer_selection.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def offer_list_selection(request):
    user_type = request.session.get('user_type')

    if user_type != 'admin':
        messages.error(request, "You need to log in as admin to access this page.")
        return redirect('login')
    return render(request, 'admin/offer_list_selection.html')