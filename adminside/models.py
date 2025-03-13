from django.db import models # type: ignore
from django.db import connection # type: ignore
from phonenumber_field.modelfields import PhoneNumberField # type: ignore
from django.contrib.auth.hashers import make_password # type: ignore
from django.contrib.auth.hashers import make_password, check_password # type: ignore 
from django.core.exceptions import ValidationError # type: ignore 
import re
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin # type: ignore
from django.contrib.auth.hashers import make_password, check_password # type: ignore
from django.utils import timezone # type: ignore
from django.utils.timezone import now  # type: ignore
from django.core.exceptions import ObjectDoesNotExist # type: ignore
from django.core.validators import RegexValidator # type: ignore


class Table(models.Model):
    STATUS_CHOICES = [
        ('vacant', 'Vacant'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
    ]

    table_id = models.AutoField(primary_key=True)
    seats = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='vacant')

    def create_tablecart_table(self):
        """Dynamically create a new table for this specific table_id."""
        print(f"DEBUG: Table ID before creating table: {self.table_id}")  # Debug print

        if not self.table_id:  # Ensure table_id is set
            print("ERROR: Table ID is not available. Skipping table creation.")
            return

        table_name = f"table_{self.table_id}_cart"  # Unique table name
        with connection.cursor() as cursor:
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                cart_id SERIAL PRIMARY KEY,
                table_id INTEGER REFERENCES adminside_table(table_id) ON DELETE CASCADE,
                order_item TEXT NOT NULL,
                size INTEGER DEFAULT 0,
                quantity INTEGER DEFAULT 0,
                price DECIMAL(10,2) DEFAULT 0.00
            )
            """
            print(f"Executing SQL Query: {query}")  # Debug print
            cursor.execute(query)

    def save(self, *args, **kwargs):
        """Override save to create a unique table dynamically."""
        super().save(*args, **kwargs)
        print(f"DEBUG: Table saved with ID {self.table_id}") 
        self.create_tablecart_table() 

    def __str__(self):
        return f"Table {self.table_id} - {self.status}"

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_firstname = models.CharField(max_length=50)
    customer_lastname = models.CharField(max_length=50)
    customer_email = models.EmailField(max_length=50, blank=True)
    customer_phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^[6789]\d{9}$', message="Phone number must be 10 digits and start with 6, 7, 8, or 9.")]
    )
    gender = models.CharField(max_length=50)



def validate_phone(value):
    phone_pattern = re.compile(r'^[6789]\d{9}$') 
    if not phone_pattern.match(value):
        raise ValidationError("Enter a valid 10-digit phone number starting with 6,7,8,9.")


class StaffManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")

        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)

        if password:
            user.set_password(password)
        else:
            raise ValueError("Password is required")

        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)

class Staff(AbstractBaseUser, PermissionsMixin):
    staff_id = models.AutoField(primary_key=True)
    staff_img = models.ImageField(upload_to='staff_images/', null=True, blank=True, default='staff_images/default.jpg')
    staff_fullname = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)  # ✅ Updated field name
    staff_email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=255)  # ✅ Django hashes password automatically
    staff_role = models.CharField(
        max_length=50, 
        choices=[("Manager", "Manager"), ("Waiter", "Waiter"), ("Chef", "Chef"), ("admin", "admin")]
    )
    staff_phone = models.CharField(max_length=15)
    branch = models.ForeignKey(
        'Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name="staff_members"
    )  

    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateField(null=True, blank=True) 
    is_active = models.BooleanField(default=True)

    objects = StaffManager()

    USERNAME_FIELD = 'username'  # ✅ Now Django will use this for authentication
    REQUIRED_FIELDS = ['staff_email']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        elif not self.password.startswith("pbkdf2_sha256$"): 
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password) 

    def __str__(self):
        return self.username

class Branch(models.Model):
    branch_id = models.AutoField(primary_key=True)
    location = models.CharField(max_length=50)
    area = models.CharField(max_length=50)
    manager = models.ForeignKey(
        "Staff", 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        limit_choices_to={'staff_role': 'Manager'}, 
        related_name="managed_branches"
    )
    phone_no = models.CharField(max_length=10, unique=True)  # Change PhoneNumberField to CharField
    is_active = models.BooleanField(default=True) 

    def clean(self):
        """ Custom validation for phone_no field """
        if not re.fullmatch(r"[6789]\d{9}$", self.phone_no):
            raise ValidationError({"phone_no": "Enter a valid 10-digit phone number starting with 6, 7, 8, or 9."})

    def __str__(self):
        return f"{self.location} - {self.area}"

class Supplier(models.Model):
  supplier_id = models.AutoField(primary_key=True)
  supplier_name = models.CharField(max_length=50)
  company_name = models.CharField(max_length=50, unique=True)
  supplier_email=models.EmailField(max_length=254)
  address= models.CharField(max_length=250)
  supplier_phone = models.CharField(max_length=10)

def get_default_supplier():
    from adminside.models import Supplier 
    return Supplier.objects.first().supplier_id if Supplier.objects.exists() else None 

class Purchase(models.Model):
    purchase_id = models.AutoField(primary_key=True)
    food_item = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)  # Added quantity field
    cost_price = models.IntegerField(null=False)
    
    supplier = models.ForeignKey(
        "Supplier", on_delete=models.CASCADE, null=True, blank=True, default=get_default_supplier
    )
    branch = models.ForeignKey("Branch", on_delete=models.SET_NULL, null=True, blank=True)
    purchased_date = models.DateField(default=now)
    
    PAYMENT_STATUS_CHOICES = [
        ("Done", "Done"),
        ("Pending", "Pending"),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"{self.food_item} ({self.quantity}) - {self.supplier.company_name if self.supplier else 'No Supplier'}"

class Categories(models.Model):
    categories_id = models.AutoField(primary_key=True)
    categories_name = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.categories_name} - {'On' if self.status else 'Off'}"

class FoodItem(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(blank=True, null=True)
    name = models.CharField(max_length=20)
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.IntegerField(null=False)
    description = models.TextField(max_length=100)
    quantity = models.IntegerField(default=1)
    is_special = models.BooleanField(default=False)  # ✅ New Column Added

    def __str__(self):
        return self.name


def delete(self, *args, **kwargs):
    """Ensure FoodItem is also deleted when Inventory is deleted"""
    FoodItem.objects.filter(name=self.name).delete()
    super().delete(*args, **kwargs)

class Inventory(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(blank=True, null=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="inventory_items")
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(max_length=100)
    stock = models.IntegerField(default=1)
    price = models.IntegerField(null=False)
    cost = models.IntegerField(null=False)
    mfg_date = models.DateField(null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.purchase.food_item} - {self.purchase.supplier.company_name if self.purchase.supplier else 'No Supplier'}"

    def save(self, *args, **kwargs):
        """Ensure FoodItem is synced with Inventory updates"""

        old_name = None
        if self.pk:  
            try:
                existing_inventory = Inventory.objects.get(pk=self.pk)
                old_name = existing_inventory.purchase.food_item
            except ObjectDoesNotExist:
                pass

        super().save(*args, **kwargs)

        if self.active:
            food_item, created = FoodItem.objects.update_or_create(
                name=self.purchase.food_item,
                defaults={
                    'image': self.image,
                    'price': self.price,
                    'category': self.category,
                    'description': self.description,
                    'quantity': self.stock,
                    'is_special': True if self.price > 500 else False
                }
            )
            if old_name and old_name != self.purchase.food_item:
                FoodItem.objects.filter(name=old_name).delete()
        
        else:
            FoodItem.objects.filter(name=self.purchase.food_item).delete()

    def delete(self, *args, **kwargs):
        FoodItem.objects.filter(name=self.purchase.food_item).delete()
        super().delete(*args, **kwargs)


def get_default_category():
    try:
        return Categories.objects.first().categories_id
    except ObjectDoesNotExist:
        return None  

class Sales_reports(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, default="Unknown Item") 
    category = models.ForeignKey(
        Categories, on_delete=models.CASCADE, related_name="sales", default=get_default_category
    )
    quantity_sold = models.IntegerField(default=1)  
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    sold_date = models.DateField(default=now) 

    def __str__(self):
        return f"{self.name} - {self.quantity_sold} Sold"