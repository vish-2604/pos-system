from django.shortcuts import render, redirect # type: ignore
from django.http import HttpResponse # type: ignore
from .forms import CustomPasswordChangeForm
from django.contrib import messages # type: ignore
from django.shortcuts import render, redirect, get_object_or_404  # type: ignore
from .forms import CustomPasswordChangeForm
from django.db import connection # type: ignore
from adminside.models import Customer,Staff,Table,Categories,FoodItem
from .forms import CustomerForm
from .models import Sales,Order
from django.contrib import messages # type: ignore
from django.utils import timezone # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib.auth import update_session_auth_hash # type: ignore
from django.contrib.messages import get_messages # type: ignore
from django.contrib.messages.storage.fallback import FallbackStorage # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
import barcode # type: ignore
from barcode.writer import ImageWriter # type: ignore
import os
from django.conf import settings # type: ignore
from decimal import Decimal
from django.db import transaction # type: ignore
from django.utils.timezone import now # type: ignore


def render_page(request, template, data=None):
    context = {
        "template": template,
        "user": request.user,
        "login_date": request.session.get("login_date"),
    }

    if request.user.is_authenticated:
        print(request.user.username)
    else:
        print("User is not authenticated")

    if data:
        context.update(data)

    return render(request, "staffside/base.html", context)

def home(request):
    messages.success(request, "✅ Login successful!")  
    return redirect('staffside:pos')
from django.db import connection # type: ignore

def pos(request):
    categories = Categories.objects.filter(status=True)
    tables = Table.objects.all()
    
    selected_category = request.GET.get("category", "all")
    selected_table = request.GET.get("table", "")  # Get selected table from URL

    try:
        selected_category = int(selected_category)
    except ValueError:
        selected_category = "all"

    food_items = FoodItem.objects.filter(category_id=selected_category) if selected_category != "all" else FoodItem.objects.all()
    
    cart_items = []
    if selected_table:
        table_cart_name = f"table_{selected_table}_cart"
        with connection.cursor() as cursor:
            try:
                query = f"SELECT cart_id, order_item, size, quantity, price FROM {table_cart_name}"
                cursor.execute(query)
                cart_items = [
                    {'cart_id': row[0], 'order_item': row[1], 'size': row[2], 'quantity': row[3], 'price': row[4]}
                    for row in cursor.fetchall()
                ]
            except Exception as e:
                print(f"Error fetching cart data: {e}")  

    return render_page(request, 'staffside/pos.html', {
        'categories': categories,
        'food_items': food_items,
        'selected_category': selected_category,
        'tables': tables,
        'selected_table': selected_table,
        'cart_items': cart_items
    })


@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        table_id = request.POST.get("table_id")
        food_item = request.POST.get("food_item")
        size = request.POST.get("size")  # Capture selected size
        quantity = int(request.POST.get("quantity", 1))
        price = float(request.POST.get("price"))

        table_cart_name = f"table_{table_id}_cart"

        with connection.cursor() as cursor:
            # Check if the same item with the same size exists
            cursor.execute(
                f"SELECT cart_id, quantity FROM {table_cart_name} WHERE order_item=%s AND size=%s",
                [food_item, size]
            )
            existing_item = cursor.fetchone()

            if existing_item:
                cart_id, existing_quantity = existing_item
                new_quantity = existing_quantity + quantity
                cursor.execute(
                    f"UPDATE {table_cart_name} SET quantity=%s WHERE cart_id=%s",
                    [new_quantity, cart_id]
                )
            cursor.execute(
                f"INSERT INTO {table_cart_name} (table_id, order_item, size, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                [table_id, food_item, size, quantity, price]
            )
        messages.success(request, "Item added to cart.")
        return redirect(f"/staffside/pos?table={table_id}&category={request.GET.get('category', 'all')}")

@csrf_exempt
def update_cart(request):
    if request.method == "POST":
        table_id = request.POST.get("table_id")
        cart_id = request.POST.get("order_item_id")
        action = request.POST.get("action")  # "increase" or "decrease"

        if not table_id or not cart_id:
            messages.error(request, "Invalid request. Missing table or cart ID.")
            return redirect(request.META.get('HTTP_REFERER', 'staffside:pos_page'))

        table_cart_name = f"table_{table_id}_cart"

        # Construct SQL queries dynamically to update the correct table
        with connection.cursor() as cursor:
            if action == "increase":
                cursor.execute(f"UPDATE {table_cart_name} SET quantity = quantity + 1 WHERE cart_id = %s", [cart_id])
            elif action == "decrease":
                cursor.execute(f"UPDATE {table_cart_name} SET quantity = GREATEST(quantity - 1, 0) WHERE cart_id = %s", [cart_id])
        
        messages.success(request, "Cart updated successfully.")
        category = request.POST.get("category", "all")
        return redirect(f"/staffside/pos?table={table_id}&category={category}")



@csrf_exempt
def remove_from_cart(request):
    if request.method == "POST":
        print(request.POST)
        table_id = request.POST.get("table_id")
        order_item_id = request.POST.get("order_item_id")

        if not table_id or not order_item_id:
            messages.error(request, "Invalid request")
            return redirect("staffside:pos")

        table_cart_name = f"table_{table_id}_cart"

        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {table_cart_name} WHERE cart_id = %s", (order_item_id,))
        
        messages.success(request, "Item removed from cart.")
        return redirect(f"/staffside/pos?table={table_id}&category={request.GET.get('category', 'all')}")

@login_required
def place_order(request):
    if request.method == "POST":
        table_id = request.POST.get("table_id")

        if not table_id:
            messages.error(request, "Please select a table before placing an order.")
            return redirect("staffside:pos")

        staff_member = request.user

        if not staff_member.branch:
            messages.error(request, "You are not assigned to any branch.")
            return redirect("staffside:pos")

        cart_table_name = f"table_{table_id}_cart"

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT order_item, size, quantity, price FROM {cart_table_name}")
            cart_items = cursor.fetchall()

        if not cart_items:
            messages.error(request, "Your cart is empty. Add items before placing an order.")
            return redirect("staffside:pos")

        table = get_object_or_404(Table, table_id=table_id)

        existing_order = Order.objects.filter(table=table, status="pending").first()

        with transaction.atomic():
            if existing_order:
                ordered_items = existing_order.ordered_items or {}  

                for item_name, size, quantity, price in cart_items:
                    key = f"{item_name}_{size}"  

                    if key in ordered_items:
                        ordered_items[key]["quantity"] += quantity  
                        ordered_items[key]["price"] += float(price)  
                    else:
                        ordered_items[key] = {"quantity": quantity, "price": float(price)}

                existing_order.total_price = float(sum(item["price"] for item in ordered_items.values()))  
                existing_order.ordered_items = ordered_items
                existing_order.save()

            else:
                ordered_items = {
                    f"{item_name}_{size}": {"quantity": quantity, "price": float(price )}
                    for item_name, size, quantity, price in cart_items
                }

                existing_order = Order.objects.create(
                    table=table,
                    ordered_items=ordered_items,
                    total_price=float(sum(item["price"]*item["quantity"] for item in ordered_items.values())),  
                    status="pending",
                    branch=staff_member.branch,
                    staff=staff_member,
                )

            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {cart_table_name}")

            table.status = "occupied"
            table.save()

        messages.success(request, f"Order placed successfully for Table {table_id}.")
        return redirect("staffside:orders")

    return redirect("staffside:pos")


def orders(request):
    user_branch = request.user.branch  
    orders = Order.objects.filter(branch=user_branch, status="pending")  
    return render_page(request, 'staffside/orders.html', {"orders": orders})

def process_payment(request):
    table_id = request.POST.get("table_id")
    if not table_id:
        messages.error(request, "Please select a table before proceeding with payment.")
        return redirect("staffside:pos")  # Redirect to POS page if no table is selected

    selected_table = Table.objects.get(table_id=table_id)

    order = Order.objects.filter(table=selected_table, status="pending").first()

    if not order:
        messages.error(request, "No pending order found for this table.")
        return redirect("staffside:pos") 

    # If order exists and is pending, confirm payment
    if order.status == "pending":
        # Record the sale in the Sales model
        sale = Sales.objects.create(
            order=order,
            payment_method="cash",  
            date=timezone.now().date(),
            time=timezone.now().time()
        )
        
        order.status = "completed"
        order.save()

        selected_table.status = "vacant"
        selected_table.save()

        messages.success(request, f"Payment successful. Sale recorded with ID: {sale.sales_id}")
        return redirect('staffside:print_bill', sale_id=sale.sales_id)

    messages.error(request, "The order has already been processed.")
    return redirect("staffside:pos")

def print_bill(request, sale_id):
    # Retrieve the Sale object using 'sales_id', not 'sale_id'
    sale = Sales.objects.get(sales_id=sale_id)

    # Define the directory to store barcodes
    barcode_dir = os.path.join(settings.MEDIA_ROOT, "barcodes")
    os.makedirs(barcode_dir, exist_ok=True)

    # Create the barcode (Code 128) based on the order ID
    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(str(sale.order.order_id), writer=ImageWriter())

    barcode_filename = f"order_{sale.order.order_id}.png"  # Add .png extension here
    barcode_path = os.path.join(barcode_dir, barcode_filename)

    options = {
        "module_width": 0.4,  # Adjust the width for better clarity
        "module_height": 10,  # Adjust the height for better clarity
        "font_size": 12  # Slightly smaller font size
    }

    # Save the barcode image
    barcode_instance.save(barcode_path, options)

    # Generate the URL for the barcode image
    barcode_url = f"{settings.MEDIA_URL}barcodes/{barcode_filename}"

    # Render the bill template
    return render_page(request, 'staffside/print_bill.html', {
        'sale': sale,
        'barcode_url': barcode_url,
        'cash_given': sale.order.total_price,
        'change': 0.00  # Assuming no change is involved for now
    })




def tables(request):
    tables=Table.objects.all()
    return render_page(request, 'staffside/tables.html',{"tables":tables})

def sales(request):
    return render_page(request, 'staffside/sales.html')

def customer(request):
    customers = Customer.objects.all()

    if request.method == 'POST':
        print("Received POST request with data:", request.POST) 

        if 'delete_customer_id' in request.POST:  
            customer_id = request.POST.get('delete_customer_id')
            customer = get_object_or_404(Customer, customer_id=customer_id)
            customer.delete()
            messages.success(request, f'Customer "{customer.customer_firstname}" deleted successfully.')
            return redirect('staffside:customer')  

        customer_id = request.POST.get('customer_id')

        form_data = request.POST.copy()
        if customer_id:
            customer = get_object_or_404(Customer, customer_id=customer_id)
            form = CustomerForm(form_data, instance=customer)
            msg = f'Customer "{customer.customer_firstname}" updated successfully.'
        else:
            form = CustomerForm(form_data)
            msg = "New customer added successfully."


        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect('staffside:customer')
        else:
            messages.error(request, "Error in form submission. Please check the fields.")

    else:
        form = CustomerForm()
    return render_page(request, 'staffside/customer.html', {"customers": customers, "form": form})

# Settings View
def staffside_settings_view(request):
    return redirect('staffside:profile')

def render_settings_page(request, template, context=None):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, template, context or {})
    context = context or {}
    context["template"] = template  
    return render(request, "staffside/settings.html", context)

# Profile View
def profile(request):
    storage = get_messages(request)
    return render_settings_page(request,"staffside/settings/profile.html",{"messages": storage})

# Change Password View
@login_required
def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "✅ Password changed successfully!")
            return redirect("staffside:profile")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render_settings_page(request, "staffside/settings/change_password.html", {'form': form})

# Update Profile View
@login_required
def update_profile_pic(request):
    if request.method == "POST" and request.FILES.get("profile_pic"):
        staff = request.user 
        staff.staff_img = request.FILES["profile_pic"]
        staff.save()
        messages.success(request, "Profile picture updated successfully!")
        return redirect("staffside:edit_profile")

    messages.error(request, "No file selected. Please try again.")
    return redirect("staffside:edit_profile")  


def edit_profile(request):
    storage = get_messages(request)
    return render_settings_page(request,"staffside/settings/edit_profile.html",{"messages": storage})