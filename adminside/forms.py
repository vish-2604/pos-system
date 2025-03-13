from django import forms # type: ignore
from django.contrib.auth.forms import PasswordChangeForm # type: ignore
from django.contrib.auth.models import User # type: ignore
from .models import Staff,Branch,Supplier,Purchase,Categories,Inventory,Customer
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
    
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            'staff_fullname', 'username', 'staff_img', 'staff_email', 
            'password', 'staff_role', 'staff_phone', 'branch', 'date_joined', 'is_active'
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
    

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_name', 'company_name', 'supplier_email', 'address', 'supplier_phone']
    

    def clean_supplier_phone(self):
        phone = str(self.cleaned_data.get('supplier_phone'))
        phone_pattern = re.compile(r'^[6789]\d{9}$')  # Ensures valid 10-digit phone numbers

        if not phone_pattern.match(phone):
            raise forms.ValidationError("Enter a valid 10-digit phone number starting with 6,7,8,9.")

        return phone

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['food_item', 'quantity', 'cost_price', 'supplier','branch', 'purchased_date', 'payment_status']
    
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=True,
        empty_label="Select a Supplier",
        label="Supplier"
    )

    payment_status = forms.ChoiceField(
        choices=Purchase.PAYMENT_STATUS_CHOICES,
        widget=forms.Select(),
        required=True,
        label="Payment Status"
    )

    def clean_cost_price(self):
        """ Validate that cost price is a positive integer """
        cost_price = self.cleaned_data.get("cost_price")
        if cost_price <= 0:
            raise forms.ValidationError("Cost price must be a positive number.")
        return cost_price

    def clean_quantity(self):
        """ Validate that quantity is a positive integer """
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive number.")
        return quantity
    

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['categories_name']

    def clean_categories_name(self):
        """Validate that category name is not empty and unique"""
        categories_name = self.cleaned_data.get("categories_name")

        if not categories_name:
            raise forms.ValidationError("Category name cannot be empty.")

        if Categories.objects.filter(categories_name__iexact=categories_name).exists():
            raise forms.ValidationError("This category already exists.")

        return categories_name

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['image', 'purchase', 'category', 'description', 'stock', 'price', 'cost', 'mfg_date', 'exp_date', 'active']

    def clean_price(self):
        """Ensure selling price is not negative."""
        price = self.cleaned_data.get("price")
        if price < 0:
            raise forms.ValidationError("Selling price cannot be negative.")
        return price

    def clean_cost(self):
        """Ensure cost price is not negative."""
        cost = self.cleaned_data.get("cost")
        if cost < 0:
            raise forms.ValidationError("Cost price cannot be negative.")
        return cost

    def clean(self):
        """Ensure manufacturing date is before expiry date."""
        cleaned_data = super().clean()
        mfg_date = cleaned_data.get("mfg_date")
        exp_date = cleaned_data.get("exp_date")

        if mfg_date and exp_date and mfg_date > exp_date:
            raise forms.ValidationError("Manufacturing date cannot be after expiry date.")

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




