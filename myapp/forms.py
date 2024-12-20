
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
        fields = ['first_name', 'last_name', 'email', 'dob', 'contact', ]

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
from .models import Booking, Employee
from django.utils import timezone

class BookingForm(forms.ModelForm):
    booking_time = forms.ChoiceField(choices=[(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(8, 20)])
    staff = forms.ModelChoiceField(queryset=Employee.objects.none(), empty_label="Preference", required=False)

    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'staff', 'additional_notes']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().strftime('%Y-%m-%d')}),
            'additional_notes': forms.Textarea(attrs={'rows': 4}), 
        }

    def __init__(self, *args, **kwargs):
        specialized_employees = kwargs.pop('specialized_employees', None)
        super().__init__(*args, **kwargs)
        if specialized_employees:
            self.fields['staff'].queryset = specialized_employees
        self.fields['staff'].label_from_instance = self.label_from_instance

    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @staticmethod
    def label_from_instance(obj):
        return f"{obj.first_name} {obj.last_name}"

    def clean_booking_date(self):
        date = self.cleaned_data.get('booking_date')
        if not date:
            raise forms.ValidationError("Booking date is required.")
        if date < timezone.now().date():
            raise forms.ValidationError("Booking date cannot be in the past.")
        if date.weekday() == 6:  # Sunday
            raise forms.ValidationError("Bookings are not available on Sundays.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        booking_time = cleaned_data.get('booking_time')
        staff = cleaned_data.get('staff')

        if booking_date and booking_time and staff:
            # Check if the employee is already booked for this time slot
            existing_bookings = Booking.objects.filter(
                staff=staff,
                booking_date=booking_date,
                booking_time=booking_time,
                status__in=['Pending', 'Confirmed']
            )
            if existing_bookings.exists():
                raise forms.ValidationError("This time slot is already booked for the selected employee. Please choose another time or employee.")

        return cleaned_data

from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }