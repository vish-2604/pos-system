from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.contrib.auth import login, logout, authenticate # type: ignore
from django.core.mail import send_mail # type: ignore
from django.conf import settings # type: ignore
from django.contrib import messages # type: ignore
from .forms import CustomLoginForm
from adminside.models import Staff
from datetime import datetime
from django.utils import timezone # type: ignore
from django.contrib.auth import authenticate # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from rest_framework.permissions import AllowAny # type: ignore
from django.contrib.auth.models import User # type: ignore
from adminside.models import Staff  # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore
from django.contrib.auth.hashers import check_password  # type: ignore



def send_confirmation_email(user, username="User"):
    subject = "Confirmation Email"
    message = f"Hi {username},\n\nYou have successfully logged into POS system."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.staff_email]  

    try:
        send_mail(subject, message, from_email, recipient_list)
        print("Verification email sent successfully!")
    except Exception as e:
        print("Failed to send verification email:", e)

def logoutaccount(request):
    logout(request)
    messages.success(request, "✅ Logout successful!")  
    return redirect('accounts:loginaccount')

def loginaccount(request): 
    if request.method == "POST": 
        print(messages) 
        form = CustomLoginForm(request.POST)  
        if not form.is_valid():  
            print("❌ Form is not valid")  
            print(form.errors)  # 🔹 Debugging errors  
            messages.error(request, "Invalid form submission.")  
            return render(request, "loginaccount.html", {"form": form})  

        username_or_email = form.cleaned_data["username_or_email"]  # ✅ Fixed  
        password = form.cleaned_data["password"]  


        user = (Staff.objects.filter(staff_email=username_or_email).first() or  
                Staff.objects.filter(username=username_or_email).first())  

        if user and check_password(password, user.password):
            send_confirmation_email(user)  
            login(request, user)  
            request.session['login_date'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')  
            if user.staff_role == "admin": 
                return redirect("adminside:home")  
            else:  
                return redirect("staffside:pos")  
        else: 
            messages.error(request, "Invalid Username or Password.")  
            return render(request, "loginaccount.html", {"form": form})  

    form = CustomLoginForm()  
    return render(request, "loginaccount.html", {"form": form})  

