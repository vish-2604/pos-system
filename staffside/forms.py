from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from adminside.models import Customer

# from .models import Profile
import re

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old Password'}),
        label="Old Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter New Password'}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
        label="Confirm Password"
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")

        if len(password) < 6:
            raise forms.ValidationError("❌ Password must be at least 6 characters long.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("❌ Password must contain at least one uppercase letter.")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("❌ Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError("❌ Password must contain at least one special character.")

        return password


    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("❌ New password and Confirm password do not match.")

        return cleaned_data
    

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_firstname', 'customer_lastname', 'customer_email', 'customer_phone', 'gender']
        widgets = {
            'gender': forms.Select(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]),
        }

    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        phone_pattern = re.compile(r'^[6789]\d{9}$')  

        if not phone_pattern.match(phone):
            raise forms.ValidationError("Enter a valid 10-digit phone number starting with 6,7,8,9.")

        return phone

    
