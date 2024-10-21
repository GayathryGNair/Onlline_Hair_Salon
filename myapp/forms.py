
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


from django import forms
from .models import Booking
import datetime

class BookingForm(forms.ModelForm):
    booking_time = forms.ChoiceField(choices=[(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(8, 20)])

    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'staff', 'additional_notes']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().strftime('%Y-%m-%d')}),
            'additional_notes': forms.Textarea(attrs={'rows': 4}), 
        }

    def __init__(self, *args, **kwargs):
        specialized_employees = kwargs.pop('specialized_employees', None)
        super().__init__(*args, **kwargs)
        if specialized_employees:
            self.fields['staff'].queryset = specialized_employees
            self.fields['staff'].empty_label = "No Preference"
        self.fields['staff'].required = False

    def clean_booking_date(self):
        date = self.cleaned_data['booking_date']
        if date < datetime.date.today():
            raise forms.ValidationError("Booking date cannot be in the past.")
        if date.weekday() == 6:  # Sunday
            raise forms.ValidationError("Bookings are not available on Sundays.")
        return date 