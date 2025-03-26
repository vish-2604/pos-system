from django.shortcuts import render, redirect # type: ignore
from django.http import HttpResponse # type: ignore
from .forms import CustomPasswordChangeForm
from django.contrib import messages # type: ignore
from django.shortcuts import render, redirect, get_object_or_404  # type: ignore
from .forms import CustomPasswordChangeForm
from django.db import connection # type: ignore
from adminside.models import Customer,Staff,Table,Categories,FoodItem,Inventory
from .forms import CustomerForm
from .models import Sales,Order,Notification,NotificationSeen
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
from django.db.models import Sum, Count # type: ignore
from datetime import date
from collections import Counter
import json  # Import JSON to ensure proper deserialization
import re
from django.http import JsonResponse # type: ignore


def render_page(request, template, data=None):
    today = timezone.now().date()

    context = {
        "template": template,
        "user": request.user,
        "login_date": request.session.get("login_date"),
        "open_notifications": request.GET.get("open_notifications") == "true"
    }

    if request.user.is_authenticated:
        # Get all notifications for today
        all_notifications = Notification.objects.filter(created_at__date=today).order_by("-created_at")

        # Get unseen notifications for the logged-in user
        unseen_notifications = all_notifications.exclude(
            notificationseen__user=request.user,
            notificationseen__seen=True
        )

        context["notifications"] = all_notifications
        context["has_unseen"] = unseen_notifications.exists()
        context["unseen_notifications"] = unseen_notifications 

        # Only mark as seen when user explicitly triggers the action
        if "mark_seen" in request.GET:
            NotificationSeen.objects.bulk_create([
                NotificationSeen(user=request.user, notification=n, seen=True)
                for n in unseen_notifications
            ], ignore_conflicts=True)

    else:
        context["notifications"] = []
        context["has_unseen"] = False

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
    search_query = request.GET.get("search", "")  # Get search query from URL

    
    selected_category = request.GET.get("category", "all")
    selected_table = request.GET.get("table", "")  # Get selected table from URL

    try:
        selected_category = int(selected_category)
    except ValueError:
        selected_category = "all"

    user_branch = request.user.branch  # Assuming User model has a 'branch' field

    if selected_category != "all":
            food_items = FoodItem.objects.filter(
                category_id=selected_category, 
                branch=user_branch,
                name__icontains=search_query  # Search by name using a case-insensitive search
            )
    else:
            food_items = FoodItem.objects.filter(
                branch=user_branch,
                name__icontains=search_query  # Search by name in all categories
            )

    
    cart_items = []
    if selected_table:
        table_cart_name = f"table_{selected_table}_cart"
        with connection.cursor() as cursor:
            try:
                query = f"SELECT cart_id, order_item, size, quantity, price,image_url FROM {table_cart_name}"
                cursor.execute(query)
                cart_items = [
                    {'cart_id': row[0], 'order_item': row[1], 'size': row[2], 'quantity': row[3], 'price': row[4],'image_url':row[5]}
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
        'cart_items': cart_items,
        'search_query': search_query,  # Pass the search query to the template

    })


@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        table_id = request.POST.get("table_id")
        food_item = request.POST.get("food_item")
        size = request.POST.get("size") 
        quantity = int(request.POST.get("quantity", 1))
        price = float(request.POST.get("price"))
        image_url = request.POST.get("image_url")

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
            else:
                # Correcting the INSERT statement
                cursor.execute(
                    f"INSERT INTO {table_cart_name} (table_id, order_item, size, quantity, price, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
                    [table_id, food_item, size, quantity, price, image_url]
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
                cursor.execute(f"UPDATE {table_cart_name} SET quantity = GREATEST(quantity - 1, 1) WHERE cart_id = %s", [cart_id])
        
        messages.success(request, "Cart updated successfully.")
        category = request.POST.get("category", "all")
        return redirect(f"/staffside/pos?table={table_id}&category={category}")



@csrf_exempt
def remove_from_cart(request):
    if request.method == "POST":
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
            cursor.execute(f"SELECT order_item, size, quantity, price, image_url FROM {cart_table_name}")
            cart_items = cursor.fetchall()

        if not cart_items:
            messages.error(request, "Your cart is empty. Add items before placing an order.")
            return redirect("staffside:pos")

        table = get_object_or_404(Table, table_id=table_id)
        existing_order = Order.objects.filter(table=table, status="pending").first()
        
        unavailable_items = []

        # ✅ Implementing FIFO-based inventory deduction
        with transaction.atomic():
            for item_name, size, quantity, price, image_url in cart_items:
                try:
                    # Fetch inventory in FIFO order (oldest first)
                    inventory_items = Inventory.objects.filter(
                        purchase__food_item=item_name, 
                        active=True
                    ).order_by('purchase__purchased_date')

                    remaining_qty = quantity  # How much we still need to deduct

                    for inventory_item in inventory_items:
                        if remaining_qty <= 0:
                            break  # Stop when deduction is complete
                        
                        if inventory_item.quantity >= remaining_qty:
                            inventory_item.quantity -= remaining_qty
                            remaining_qty = 0
                        else:
                            remaining_qty -= inventory_item.quantity
                            inventory_item.quantity = 0
                            inventory_item.active = False  # Mark inactive if out of stock

                        inventory_item.save()

                    if remaining_qty > 0:
                        unavailable_items.append(item_name)

                except Inventory.DoesNotExist:
                    unavailable_items.append(item_name)

            if unavailable_items:
                messages.error(request, f"Stock unavailable for: {', '.join(unavailable_items)}")
                return redirect("staffside:pos")
             
            # ✅ Handling existing order
            if existing_order:
                ordered_items = existing_order.ordered_items or {}
                existing_image_urls = existing_order.image_urls or []

                
                for item_name, size, quantity, price, image_url in cart_items:
                    key = f"{item_name}_{size}"
                    
                    if key in ordered_items:
                        ordered_items[key]["quantity"] += quantity
                    else:
                        ordered_items[key] = {"quantity": quantity, "price": float(price)}  # ✅ Correct: Store per-item price
                        if item_name not in [name.split("_")[0] for name in ordered_items.keys()]:
                            existing_image_urls.append(image_url)

                existing_order.total_amount = float(sum(item["price"] * item["quantity"] for item in ordered_items.values()))
                existing_order.ordered_items = ordered_items
                existing_order.image_urls = existing_image_urls
                existing_order.save()
            else:
                ordered_items = {
                    f"{item_name}_{size}": {"quantity": quantity, "price": float(price)}
                    for item_name, size, quantity, price, _ in cart_items
                }

                image_urls = [image_url for _, _, _, _, image_url in cart_items]

                existing_order = Order.objects.create(
                    table=table,
                    ordered_items=ordered_items,
                    total_amount=float(sum(item["price"] * item["quantity"] for item in ordered_items.values())),
                    status="pending",
                    branch=staff_member.branch,
                    staff=staff_member,
                    image_urls=image_urls,
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
    discount_percentage = request.POST.get("discount_percentage", "").strip()

    if not table_id:
        messages.error(request, "Please select a table before proceeding with payment.")
        return redirect("staffside:pos")

    selected_table = Table.objects.get(table_id=table_id)
    order = Order.objects.filter(table=selected_table, status="pending").first()

    if not order:
        messages.error(request, "No pending order found for this table.")
        return redirect("staffside:pos")

    try:
        discount_percentage = float(discount_percentage) if discount_percentage else 0.0
    except ValueError:
        messages.error(request, "Invalid discount percentage entered.")
        return redirect("staffside:pos")

    discount_amount = (discount_percentage / 100) * order.total_amount  
    final_total = order.total_amount - discount_amount  

    if order.status == "pending":
        sale = Sales.objects.create(
            order=order,
            payment_method="cash",
            date=timezone.now().date(),
            time=timezone.localtime().time()
        )

        order.discount_percentage = discount_percentage
        order.discount_amount = discount_amount
        order.final_total = final_total
        order.status = "completed"
        order.save()

        selected_table.status = "vacant"
        selected_table.save()

        messages.success(request, f"Payment successful. Sale recorded with ID: {sale.sales_id}")
        return redirect('staffside:print_bill', sale_id=sale.sales_id)

    messages.error(request, "The order has already been processed.")
    return redirect("staffside:pos")


def print_bill(request, sale_id):
    sale = Sales.objects.get(sales_id=sale_id)

    barcode_dir = os.path.join(settings.MEDIA_ROOT, "barcodes")
    os.makedirs(barcode_dir, exist_ok=True)

    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(str(sale.order.order_id), writer=ImageWriter())

    barcode_filename = f"order_{sale.order.order_id}.png"
    barcode_path = os.path.join(barcode_dir, barcode_filename)

    options = {
        "module_width": 0.4,
        "module_height": 10,
        "font_size": 12
    }

    barcode_instance.save(barcode_path[:-4], options)  # Remove extra .png

    barcode_url = f"{settings.MEDIA_URL}barcodes/{barcode_filename}"

    return render_page(request, 'staffside/print_bill.html', {
        'sale': sale,
        'barcode_url': barcode_url,
        'change': 0.00
    })


def tables(request):
    tables = Table.objects.all()
    orders = Order.objects.filter(status="pending")  # Fetch only pending orders

    orders_by_table = {order.table.table_id: order for order in orders}

    if request.method == "POST":
        table_id = request.POST.get('table_id')
        status = request.POST.get('status')  # Get the status from the form

        if table_id.startswith('T-'):
            table_id = table_id[2:]

        try:
            table = Table.objects.get(table_id=table_id)
            table.status = status if status else 'vacant'
            table.save()
        except Table.DoesNotExist:
            pass

        return redirect('staffside:tables')

    return render_page(request, 'staffside/tables.html', {
        "tables": tables,
        "orders_by_table": orders_by_table
    })

from django.utils.timezone import localtime # type: ignore

def sales(request):
    user = request.user
    today = date.today()
    
    sales_today = Sales.objects.filter(order__branch=user.branch, date=today)
    total_sales = sales_today.aggregate(total=Sum('order__total_amount'))['total'] or 0
    num_orders = sales_today.count()
    total_discounts = sales_today.aggregate(total=Sum('order__discount_amount'))['total'] or 0  

    item_counter = Counter()

    for sale in sales_today:
        if sale.order and sale.order.ordered_items:
            # Ensure ordered_items is a dictionary (convert from string if needed)
            if isinstance(sale.order.ordered_items, str):
                ordered_items = json.loads(sale.order.ordered_items)  # Convert string to dict
            else:
                ordered_items = sale.order.ordered_items  # Already a dictionary
            
            # Process items
            for item_name, details in ordered_items.items():
                # Extract base item name (Remove _small, _medium, _large)
                base_item = re.sub(r'_(small|medium|large)$', '', item_name)
                item_counter[base_item] += details["quantity"]

    # Get the best-selling item
    best_selling_item = item_counter.most_common(1)
    best_selling_item = best_selling_item[0][0] if best_selling_item else "No Sales"

    context = {
        "sales": sales_today,
        "total_sales": total_sales,
        "num_orders": num_orders,
        "total_discounts": total_discounts,
        "best_selling_item": best_selling_item,
    }
    
    return render_page(request, 'staffside/sales.html', context)


def customer(request):
    customers = Customer.objects.all()

    if request.method == 'POST':
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