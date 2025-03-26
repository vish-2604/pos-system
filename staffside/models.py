from django.utils.timezone import localtime # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.db import models # type: ignore
from django.utils.timezone import now  # type: ignore 
from django.utils import timezone # type: ignore
from adminside.models import Table,Branch,Staff  # Ensure this is correctly imported
from django.conf import settings # type: ignore
import pytz # type: ignore


class Order(models.Model):

    order_id = models.AutoField(primary_key=True)  # Auto-incremented primary key
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    ordered_items = models.JSONField(default=dict)  # Stores items, quantity, and per-item price
    total_amount = models.FloatField(default=0.0)  # Original total before discount
    discount_percentage = models.FloatField(default=0.0)  # Discount %
    discount_amount = models.FloatField(default=0.0)  # Discounted amount
    final_total = models.FloatField(default=0.0)  # Total after discount
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")  # ✅ Set NULL instead of delete
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")  
    status = models.CharField(
        max_length=10,
        choices=[("pending", "Pending"), ("completed", "Completed")],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Stores order creation timestamp
    image_urls = models.JSONField(default=list, blank=True, null=True)  # Store images as JSON


    def __str__(self):
        return f"Order {self.order_id} - Table {self.table.table_id} - {self.status}"

    def calculate_total_price(self):
        """Calculate total price based on ordered items"""
        self.total_price = sum(item["price"] * item["quantity"] for item in self.ordered_items.values())
        self.save()


def get_ist_time():
    return localtime().time()

class Sales(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
    ]

    sales_id = models.AutoField(primary_key=True)  # Auto-incremented Sale ID
    order = models.ForeignKey('Order', on_delete=models.CASCADE, default=None, null=True, blank=True)  
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')  
    date = models.DateField(default=now)
    time = models.TimeField(default=get_ist_time)  # ✅ Fixed time field


    def __str__(self):
        return f"Sale {self.sales_id} - Order {self.order.order_id if self.order else 'N/A'} ({self.payment_method})"



class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Who created the notification
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"

class NotificationSeen(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)  # Which notification
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Who saw it
    seen = models.BooleanField(default=False)
    seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('notification', 'user')  # Prevent duplicate seen records

    def __str__(self):
        return f"{self.user.username} - Seen: {self.seen}"

    