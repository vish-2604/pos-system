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


def send_confirmation_email(recipient, username="User"):
    subject = "Confirmation Email"
    message = f"Hi {username},\n\nYou have successfully logged into POS system."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [recipient]  

    try:
        send_mail(subject, message, from_email, recipient_list)
        print("Verification email sent successfully!")
    except Exception as e:
        print("Failed to send verification email:", e)


def logoutaccount(request):        
    logout(request)
    return redirect('loginaccount') 


def loginaccount(request):
    if request.method == "POST":
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            staff = form.cleaned_data["staff"]

            # Authenticate the user using Django's default authentication
            user = authenticate(request, username=staff.staff_username, password=form.cleaned_data['password'])

            if user is not None:
                # Log the user in (this will handle the session automatically)
                login(request, user)

                # Set login date in session
                request.session['login_date'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

                # Redirect based on the staff role
                if user.staff_role == "admin":
                    return redirect("adminside:home")
                else:
                    return redirect("staffside:pos")
            else:
                messages.error(request, "Invalid Username or Password.")
    
    form = CustomLoginForm()
    return render(request, "loginaccount.html", {"form": form})

