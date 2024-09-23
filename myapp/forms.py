# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import users

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = users
        fields = ['email', 'password', 'contact', 'status']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if users.objects.filter(email=email).exists():
            raise ValidationError("Email is already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if not contact.isdigit() or len(contact) < 10:
            raise ValidationError("Contact number must be at least 10 digits long.")
        return contact

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        # Add any additional cross-field validation if necessary
