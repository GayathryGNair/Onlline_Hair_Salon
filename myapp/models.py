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


from django.db import models
from django.contrib.auth.hashers import make_password
from datetime import datetime

class Employee(User):
    reset_token = models.CharField(max_length=64, null=True, blank=True)
    approved = models.BooleanField(default=False)
    specializations = models.ManyToManyField('Specialization', blank=True)
    qualification_certificate = models.FileField(upload_to='employee_certificates/', null=True, blank=True)
    is_on_leave = models.BooleanField(default=False)
    leave_start = models.DateTimeField(null=True, blank=True)
    leave_end = models.DateTimeField(null=True, blank=True)

    def is_available(self, date, time):
        if self.is_on_leave:
            if self.leave_start <= datetime.combine(date, time) <= self.leave_end:
                return False
        return True

class EmployeeAvailability(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=[(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])])
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('employee', 'day_of_week')
    def is_specialist_for(self, service):
        return self.specializations.filter(servicecategory__servicesubcategory__service=service).exists()

class Specialization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_categories')

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
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    preffered_date = models.DateField()
    preffered_time = models.TimeField()
    staff = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')
    additional_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Booking for {self.service.service_name} by {self.client.first_name} on {self.booking_date.strftime('%Y-%m-%d %H:%M:%S')}"

    @property
    def subcategory(self):
        return self.service.subcategory  # Accessing the subcategory through the service

    @property
    def category(self):
        return self.service.subcategory.category  # Accessing the category through the subcategory



