from django import forms # type: ignore
from django.contrib.auth.forms import PasswordChangeForm # type: ignore
from django.contrib.auth.models import User # type: ignore
from .models import Staff,Branch
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

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")

        # Password must be at least 6 characters long
        if len(password) < 6:
            raise forms.ValidationError("❌ Password must be at least 6 characters long.")

        # At least one uppercase letter
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("❌ Password must contain at least one uppercase letter.")

        # At least one digit
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("❌ Password must contain at least one digit.")

        # At least one special character
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
    
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            'staff_fullname', 'staff_username', 'staff_img', 'staff_email', 
            'staff_password', 'staff_role', 'staff_phone', 'branch', 'date_joined', 'is_active'
        ]
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.Select(choices=[(True, 'Active'), (False, 'Inactive')]),
        }


    def clean_staff_phone(self):
        phone = self.cleaned_data.get('staff_phone')
        phone_pattern = re.compile(r'^[6789]\d{9}$')  

        if not phone_pattern.match(phone):
            raise forms.ValidationError("Enter a valid 10-digit phone number starting with 6,7,8,9.")

        return phone


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['location', 'area', 'manager', 'phone_no', 'is_active']
        widgets = {
            'is_active': forms.Select(choices=[('Active', 'Active'), ('Inactive', 'Inactive')]),
        }

    manager = forms.ModelChoiceField(queryset=Staff.objects.filter(staff_role="Manager"), required=False)
    
    def clean_phone_no(self):
        phone = str(self.cleaned_data.get('phone_no'))
        phone_pattern = re.compile(r'^[6789]\d{9}$')  # Ensures valid 10-digit phone numbers

        if not phone_pattern.match(phone):
            raise forms.ValidationError("Enter a valid 10-digit phone number starting with 6,7,8,9.")

        return phone

