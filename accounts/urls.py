from django.urls import path # type: ignore
from . import views

app_name="accounts"

urlpatterns = [
   path('', views.loginaccount, name='loginaccount'),
   path('logout/', views.logoutaccount, name='logoutaccount'),
]