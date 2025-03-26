from django.contrib import admin
from .models import Order,Sales,Notification,NotificationSeen

admin.site.register(Order)
admin.site.register(Sales)
admin.site.register(Notification)
admin.site.register(NotificationSeen)