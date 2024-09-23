# myapp/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import users
from django.contrib.auth.hashers import check_password
from .forms import RegistrationForm
from django.contrib.auth import logout as auth_logout
from django.views.decorators.cache import cache_control
from django.core.mail import EmailMessage, send_mail
from django.utils.crypto import get_random_string
from django.urls import reverse


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
        user = users.objects.filter(email=email).first()
        
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
    user = users.objects.filter(reset_token=token).first()
    
    if user:
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password == confirm_password:
                # Hash the new password before saving it
                user.password = new_password
                
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
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        status = request.POST['status']

        try:
            user = users.objects.get(email=email, status=status)
            if check_password(password, user.password):
                # Set session variables to manage the user login status
                request.session['user_id'] = user.id
                request.session['user_email'] = user.email
                request.session['user_status'] = user.status
                messages.success(request, 'Login successful!')

                # Redirect based on user status
                if user.status == 'store':
                    return redirect('store_dashboard')
                elif user.status == 'employee':
                    return redirect('employee_dashboard')
                elif user.status == 'client':
                    return redirect('client_dashboard')
            else:
                messages.error(request, 'Invalid password.')
        except users.DoesNotExist:
            messages.error(request, 'User with provided email and status does not exist.')
    
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('register')  # Redirect as needed
        else:
            # Form is invalid, so render the form with error messages
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def for_men(request):
    return render(request, 'for_men.html')

def for_women(request):
    return render(request, 'for_women.html')

def store_dashboard(request):
    if request.session.get('user_status') != 'store':
        return redirect('login')
    return render(request, 'client_dashboard.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def employee_dashboard(request):
    if request.session.get('user_status') != 'employee':
        return redirect('login')
    return render(request, 'employee_dashboard.html')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def client_dashboard(request):
    if request.session.get('user_status') != 'client':
        return redirect('login')
    return render(request, 'client_dashboard.html')

