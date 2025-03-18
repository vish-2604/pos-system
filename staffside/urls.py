from django.urls import path # type: ignore
from . import views

app_name = "staffside"

urlpatterns = [
    path('', views.home, name='home'),
    path('place_order/',views.place_order,name='place_order'),
    path('orders/', views.orders, name='orders'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('print-bill/<int:sale_id>/', views.print_bill, name='print_bill'),
    path('tables/', views.tables, name='tables'),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("remove_from_cart/", views.remove_from_cart, name="remove_from_cart"),
    path("update_cart/", views.update_cart, name="update_cart"),
    path('pos/', views.pos, name='pos'),
    path('sales/', views.sales, name='sales'),
    path('customer/', views.customer, name='customer'),
    path('settings/', views.staffside_settings_view, name='settings'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path("update-profile-pic/", views.update_profile_pic, name="update_profile_pic"),
    path('change_password/', views.change_password, name='change_password'),
]


