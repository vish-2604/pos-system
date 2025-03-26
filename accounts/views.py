from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.contrib.auth import login, logout, authenticate # type: ignore
from django.core.mail import send_mail # type: ignore
from django.conf import settings # type: ignore
from django.contrib import messages # type: ignore
from .forms import CustomLoginForm,PasswordResetForm
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
import random
from django.http import JsonResponse # type: ignore
from twilio.rest import Client  # type: ignore # Import Twilio client
from django.contrib.auth.hashers import make_password # type: ignore
import re

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
                return redirect("staffside:home")  
        else: 
            messages.error(request, "Invalid Username or Password.")  
            return render(request, "loginaccount.html", {"form": form})  

    form = CustomLoginForm()  
    return render(request, "loginaccount.html", {"form": form})  


otp_storage = {}

def send_otp(email_or_phone, otp):
    """
    Function to send OTP via Email or SMS.
    """
    subject = "Your Password Reset OTP"
    message = f"Your OTP for password reset is: {otp}. Do not share this with anyone."

    if "@" in email_or_phone:
        # Send OTP via Email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email_or_phone])
    else:
        pass

def request_password_reset(request):
    """
    View to handle password reset requests.
    """
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email_or_phone = form.cleaned_data["email_or_phone"]
            user = Staff.objects.filter(staff_email=email_or_phone).first() or \
                   Staff.objects.filter(staff_phone=email_or_phone).first()

            if user:
                otp = random.randint(100000, 999999)  # Generate 6-digit OTP
                otp_storage[email_or_phone] = otp  # Store OTP temporarily
                
                send_otp(email_or_phone, otp)
                
                request.session["reset_email_or_phone"] = email_or_phone  # Store user identifier
                return redirect("accounts:verify_otp")  # Redirect to OTP verification page

    else:
        form = PasswordResetForm()

    return render(request, "password_reset.html", {"form": form})

def verify_otp(request):
    """
    View to verify OTP.
    """
    if request.method == "POST":
        email_or_phone = request.session.get("reset_email_or_phone")
        entered_otp = request.POST.get("otp")

        if not email_or_phone or email_or_phone not in otp_storage:
            messages.error(request, "Session expired. Please request password reset again.")
            return redirect("accounts:request_password_reset")

        # Validate OTP input (check if it contains only digits and is 6 digits long)
        if not entered_otp.isdigit() or len(entered_otp) != 6:
            messages.error(request, "Invalid OTP format. Please enter a 6-digit number.")
            return redirect("accounts:verify_otp")

        if otp_storage[email_or_phone] == int(entered_otp):
            del otp_storage[email_or_phone]  # Remove OTP after verification
            request.session["otp_verified"] = True
            return redirect("accounts:reset_password")  # Redirect to password reset page
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "verify_otp.html")



def validate_password_strength(password):
    """
    Checks if password meets security requirements.
    """
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    if not re.search(r"[A-Z]", password):  # At least one uppercase
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):  # At least one lowercase
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):  # At least one digit
        return "Password must contain at least one digit."
    if not re.search(r"[@$!%*?&]", password):  # At least one special character
        return "Password must contain at least one special character (@, $, !, etc.)."
    return None  # No errors, password is valid

def reset_password(request):
    """
    View to reset the password after OTP verification.
    """
    if not request.session.get("otp_verified"):
        messages.error(request, "OTP verification required.")
        return redirect("accounts:request_password_reset")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Check if passwords match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "reset_password.html")

        # Validate password strength
        password_error = validate_password_strength(new_password)
        if password_error:
            messages.error(request, password_error)
            return render(request, "reset_password.html")

        email_or_phone = request.session.get("reset_email_or_phone")
        user = Staff.objects.filter(staff_email=email_or_phone).first() or \
               Staff.objects.filter(staff_phone=email_or_phone).first()

        if user:
            user.password = make_password(new_password)  # Hash the new password
            user.save()
            del request.session["otp_verified"]  # Clear session
            messages.success(request, "Password reset successfully.")
            return redirect("accounts:loginaccount")

    return render(request, "reset_password.html")

