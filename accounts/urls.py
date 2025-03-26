from django.urls import path # type: ignore
from . import views

app_name="accounts"

urlpatterns = [
   path('', views.loginaccount, name='loginaccount'),
   path('logout/', views.logoutaccount, name='logoutaccount'),
   path("password-reset/", views.request_password_reset, name="request_password_reset"),
   path("verify-otp/", views.verify_otp, name="verify_otp"),
   path("reset-password/", views.reset_password, name="reset_password"),
]