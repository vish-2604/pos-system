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

class Purchase(models.Model):
    food_item_id=models.AutoField(primary_key=True)
    food_item=models.CharField(max_length=50)
    cost_price=models.IntegerField(null=False)
    supplier_id=models.IntegerField(null=False)
    purchased_date=models.DateField()
    payment_status=models.CharField(max_length=10)

class Inventory(models.Model):
    food_item_id=models.AutoField(primary_key=True)
    image=models.ImageField(blank=True)
    food_item_name=models.CharField(max_length=20)
    category=models.CharField(max_length=20)
    description=models.TextField(max_length=100)
    quantity=models.IntegerField(null=True)
    branch=models.CharField(max_length=20)
    sell_price=models.IntegerField(null=False)
    cost_price=models.IntegerField(null=False)
    mfg_date=models.DateField()
    exp_date=models.DateField()

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


class Sales_reports(models.Model):
  product_id = models.AutoField(primary_key=True)
  product_name = models.CharField(max_length=50)
  categories= models.CharField(max_length=50)
  quantities= models.IntegerField()
  
class Supplier(models.Model):
  supplier_id = models.AutoField(primary_key=True)
  supplier_name = models.CharField(max_length=50)
  company_name = models.CharField(max_length=50)
  supplier_email=models.EmailField(max_length=254)
  supplier_phone=PhoneNumberField()
  address= models.CharField(max_length=250)
  branch=models.CharField(max_length=50) 

class Categories(models.Model):
  categories_id = models.AutoField(primary_key=True)
  categories_name = models.CharField(max_length=50)
  status= models.CharField(max_length=20)

class Customer(models.Model):
  customer_id = models.AutoField(primary_key=True)
  customer_firstname = models.CharField(max_length=50)
  customer_lastname = models.CharField(max_length=50)
  customer_email=models.EmailField(max_length=20,blank=True)
  customer_phone=PhoneNumberField()
  gender=models.CharField(max_length=50)


def validate_phone(value):
    phone_pattern = re.compile(r'^[6789]\d{9}$')  # 10-digit number starting with 6,7,8,9
    if not phone_pattern.match(value):
        raise ValidationError("Enter a valid 10-digit phone number starting with 6,7,8,9.")

class StaffManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(staff_username=username, **extra_fields)
        user.set_password(password)
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
    staff_username = models.CharField(max_length=50, unique=True)
    staff_email = models.EmailField(max_length=50, unique=True)
    staff_password = models.CharField(max_length=255)
    staff_role = models.CharField(
        max_length=50, 
        choices=[("Manager", "Manager"), ("Waiter", "Waiter"), ("Chef", "Chef")]
    )
    staff_phone = models.CharField(max_length=15)
    branch = models.ForeignKey(
        'Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name="staff_members"
    )  

    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateField(null=True, blank=True) 
    is_active = models.BooleanField(default=True)

    objects = StaffManager()

    USERNAME_FIELD = 'staff_username'
    REQUIRED_FIELDS = ['staff_email']

    def save(self, *args, **kwargs):
        if self.date_joined is None:
            self.date_joined = timezone.now().date()

        if not self.staff_password.startswith("pbkdf2_sha256$"):
            self.staff_password = make_password(self.staff_password)
        
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.staff_password)

    def __str__(self):
        return self.staff_username




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


