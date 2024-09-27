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
    reset_token = models.CharField(max_length=64, null=True, blank=True)  # Add reset_token field

from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)  # Name of the service
    description = models.TextField()  # Description of the service
    rate = models.DecimalField(max_digits=8, decimal_places=2)  # Price of the service
    duration = models.DurationField(help_text="Duration in HH:MM:SS format")  # Duration of the service

    def __str__(self):
        return self.name
