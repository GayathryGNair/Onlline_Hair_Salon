# forms.py
from django import forms
from .models import Client

class ClientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'dob', 'contact']
class EmployeeProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'dob', 'contact']
from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'rate', 'duration']
