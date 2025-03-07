from django import forms  # type: ignore
from django.contrib.auth.hashers import check_password  # type: ignore
from django.core.exceptions import ValidationError  # type: ignore
from adminside.models import Staff  # type: ignore

class CustomLoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get("username_or_email")
        password = cleaned_data.get("password")

        if username_or_email and password:
            staff = Staff.objects.filter(staff_email=username_or_email).first() or Staff.objects.filter(staff_username=username_or_email).first()
            
            if not staff:
                raise ValidationError("Invalid Username or Email.")

            if not staff.check_password(password):  # Use the check_password method from model
                raise ValidationError("Incorrect Password.")

            cleaned_data["staff"] = staff  # Store staff object for login view

        return cleaned_data
