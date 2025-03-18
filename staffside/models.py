from django.db import models # type: ignore
from django.utils.timezone import now  # type: ignore 
from django.utils import timezone # type: ignore
from adminside.models import Table,Branch,Staff  # Ensure this is correctly imported

class Order(models.Model):

    order_id = models.AutoField(primary_key=True)  # Auto-incremented primary key
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    ordered_items = models.JSONField(default=dict)  # Stores items, quantity, and per-item price
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # ✅ Total order price
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="orders")  # ✅ Store location
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")  
    status = models.CharField(
        max_length=10,
        choices=[("pending", "Pending"), ("completed", "Completed")],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Stores order creation timestamp

    def __str__(self):
        return f"Order {self.order_id} - Table {self.table.table_id} - {self.status}"

    def calculate_total_price(self):
        """Calculate total price based on ordered items"""
        self.total_price = sum(item["price"] * item["quantity"] for item in self.ordered_items.values())
        self.save()

class Sales(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
    ]

    sales_id = models.AutoField(primary_key=True)  # Auto-incremented Sale ID
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=None, null=True, blank=True)  # Default None
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')  
    date = models.DateField(default=now)
    time = models.TimeField(default=now) 

    def __str__(self):
        return f"Sale {self.sales_id} - Order {self.order.order_id if self.order else 'N/A'} ({self.payment_method})"



    