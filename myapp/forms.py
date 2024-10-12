
from django import forms
from .models import Client

class ClientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'dob', 'contact']

    def __init__(self, *args, **kwargs):
        super(ClientProfileUpdateForm, self).__init__(*args, **kwargs)
        # Make the email field read-only
        self.fields['email'].widget.attrs['readonly'] = True

class EmployeeProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'dob', 'contact']

    def __init__(self, *args, **kwargs):
        super(EmployeeProfileUpdateForm, self).__init__(*args, **kwargs)
        # Make the email field read-only
        self.fields['email'].widget.attrs['readonly'] = True


from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'description', 'rate', 'image', 'subcategory']


