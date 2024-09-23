# models.py
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import make_password, check_password as django_check_password


class users(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    status = models.CharField(max_length=10, choices=[('store', 'Store/Salon'), ('employee', 'Employee'), ('client', 'Client')])
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.email
     
    def save(self, *args, **kwargs):
        if not self.pk or not self.password.startswith('pbkdf2_sha256$'):  # Ensures the password is hashed only once
            self.password = make_password(self.password)
        super(users, self).save(*args, **kwargs)

from django.db import models

class Booking(models.Model):
    SERVICE_CHOICES = [
        ('hair_wash', 'Hair Wash'),
        ('hair_colour', 'Hair Colour'),
        ('hair_spa', 'Hair Spa'),
        # Add other services as needed
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    stylist = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"{self.name} - {self.service} on {self.date} at {self.time}"
