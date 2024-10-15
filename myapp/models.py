from django.db import models
from django.contrib.auth.hashers import make_password

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    dob = models.DateField()
    contact = models.CharField(max_length=15)
    status = models.BooleanField(default=True)

    is_super = models.BooleanField(default=False)


    class Meta:
        abstract = True

class Client(User):
    reset_token = models.CharField(max_length=64, null=True, blank=True)  # Add reset_token field

class Employee(User):
    
    reset_token = models.CharField(max_length=64, null=True, blank=True) 
    approved = models.BooleanField(default=False)  # Add reset_token field

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ServiceSubcategory(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True) 
    image = models.ImageField(upload_to='servicesubcategory_images/', blank=True, null=True)
    

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Service(models.Model):
    subcategory = models.ForeignKey(ServiceSubcategory, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Rate in Indian Rupees")
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.service_name} ({self.subcategory.name} - {self.subcategory.category.name})"
    
from django.db import models
from django.utils import timezone

class Booking(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Link to the Client model
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  # Link to Service
    booking_date = models.DateTimeField(auto_now_add=True)  # Date and time of booking
    preferred_date = models.DateField(null=True, blank=True)  # Preferred date for the service
    preferred_time = models.TimeField(null=True, blank=True)  # Preferred time for the service
    staff = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)  # Link to the Employee (staff)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')  # Status of the booking
    additional_notes = models.TextField(blank=True, null=True)  # Optional additional notes

    def __str__(self):
        return f"Booking for {self.service.service_name} by {self.client.first_name} on {self.booking_date.strftime('%Y-%m-%d %H:%M:%S')}"

    @property
    def subcategory(self):
        return self.service.subcategory  # Accessing the subcategory through the service

    @property
    def category(self):
        return self.service.subcategory.category  # Accessing the category through the subcategory



from django.db import models
from .models import Employee  # Make sure to import your Employee model

class Interview(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='interviews')
    interview_date = models.DateField(null=False)
    starting_time = models.TimeField()
    ending_time = models.TimeField()
    meeting_link = models.URLField(max_length=200)
    interviewer_name = models.CharField(max_length=150)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Interview for {self.employee.first_name} {self.employee.last_name} on {self.interview_date}"
