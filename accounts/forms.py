from django import forms  
from django.contrib.auth.hashers import check_password  
from adminside.models import Staff  

class CustomLoginForm(forms.Form):  
    username_or_email = forms.CharField(  
        label="Username or Email",  
        widget=forms.TextInput(attrs={"class": "form-control"}),  
    )  
    password = forms.CharField(  
        label="Password",  
        widget=forms.PasswordInput(attrs={"class": "form-control"}),  
    )  

    def clean(self):  
        cleaned_data = super().clean()  
        username_or_email = cleaned_data.get("username_or_email")  
        password = cleaned_data.get("password")  

        if username_or_email and password:  
            staff = (  
                Staff.objects.filter(staff_email=username_or_email).first()  
                or Staff.objects.filter(username=username_or_email).first()  
            )  

            if not staff:  
                self.add_error("username_or_email", "Invalid Username or Email.")  
                return cleaned_data  

            if not check_password(password, staff.password): 
                print(password) 
                print(staff.password)
                self.add_error("password", "Incorrect Password.")  
                return cleaned_data  

            cleaned_data["staff"] = staff  

        return cleaned_data  
