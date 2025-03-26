from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404  # type: ignore
from .forms import CustomPasswordChangeForm
from django.db import connection # type: ignore
from .models import Staff,Branch,Supplier,Purchase,Categories,Inventory,FoodItem,Table,Customer,Sales_reports
from .forms import StaffForm,BranchForm,SupplierForm,PurchaseForm,CategoryForm,InventoryForm,CustomerForm
from django.contrib import messages # type: ignore
from django.utils import timezone # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib.auth import update_session_auth_hash # type: ignore
from django.contrib.messages import get_messages # type: ignore
from django.contrib.messages.storage.fallback import FallbackStorage # type: ignore
from staffside.models import Sales,Notification,NotificationSeen,Order
from django.utils.timezone import now # type: ignore
from datetime import datetime
from datetime import date
from django.conf import settings # type: ignore
from django.utils import timezone # type: ignore
from collections import defaultdict
from django.db.models import Sum, Count # type: ignore
from datetime import datetime, timedelta
import random
from django.db.models.functions import TruncMonth # type: ignore


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

    return render(request, "adminside/base.html", context)

# Home View
def home(request):
    messages.success(request, "✅ Login successful!")  
    return redirect("adminside:dashboard")

def dashboard(request):
    # --- Total Orders ---
    total_orders = Order.objects.count()

    # --- Count Unique Customers (Using 'Table' as Customer Representation) ---
    total_customers = Customer.objects.count()

    # --- Total Sales Revenue ---
    total_sales = Sales.objects.aggregate(total=Sum('order__final_total'))['total'] or 0

    # --- Total Purchases (All-Time) ---
    total_cost = Purchase.objects.aggregate(total_cost=Sum('cost_price'))['total_cost'] or 0

    # --- Profit Calculation (All-Time) ---
    total_profit = total_sales - total_cost


    
    # --- Weekly Sales (If Needed) ---
    last_week = datetime.today() - timedelta(days=7)
    weekly_sales = (
        Sales.objects.filter(date__gte=last_week)
        .aggregate(total=Sum('order__final_total'))['total'] or 0
    )

    # --- Sales Analytics Data ---
    today = datetime.today()
    last_week = today - timedelta(days=7)
    sales_data = (
        Sales.objects
        .filter(date__gte=last_week)  # ✅ Use `date` instead of `purchased_date`
        .values('date')
        .annotate(total=Sum('order__final_total'))
        .order_by('date')
    )

    sales_labels = [data['date'].strftime('%Y-%m-%d') for data in sales_data]
    sales_values = [data['total'] for data in sales_data]

    # --- Best Selling Items (Top 5, Grouped by Base Name) ---
    best_selling_items = Order.objects.values_list('ordered_items', flat=True)
    item_count = defaultdict(lambda: {"quantity": 0, "total_price": 0, "image": "", "price": 0})

    for items in best_selling_items:
        for item_name, details in items.items():
            base_name = item_name.split('_')[0]  # Extract base name

            if base_name in item_count:
                item_count[base_name]["quantity"] += details["quantity"]
                item_count[base_name]["total_price"] += details["quantity"] * details["price"]
            else:
                item_instance = Inventory.objects.filter(purchase__food_item__icontains=base_name).first()

                item_count[base_name] = {
                    "quantity": details["quantity"],
                    "total_price": details["quantity"] * details["price"],
                    "image": item_instance.image.url if item_instance and item_instance.image else "/static/images/default.png",
                    "price": details["price"],
                }

    sorted_items = sorted(item_count.items(), key=lambda x: x[1]["quantity"], reverse=True)[:5]

    top_items = [
        {"name": item[0], "quantity": item[1]["quantity"], "total_price": item[1]["total_price"], "image": item[1]["image"], "price": item[1]["price"]}
        for item in sorted_items
    ]

    # Monthly Sales Revenue
    monthly_profit_data = (
        Sales.objects.annotate(month=TruncMonth('date'))  # Extract month from `date`
        .values('month')
        .annotate(revenue=Sum('order__final_total'))
        .order_by('month')
    )

    # Monthly Costs
    monthly_cost_data = (
        Purchase.objects.annotate(month=TruncMonth('purchased_date'))
        .values('month')
        .annotate(cost=Sum('cost_price'))
        .order_by('month')
    )

    # Convert Monthly Costs to Dictionary for Quick Lookup
    cost_dict = {data['month']: data['cost'] for data in monthly_cost_data}

    # Compute Monthly Profit (Revenue - Cost)
    profit_trend_labels = [data['month'].strftime('%Y-%m') for data in monthly_profit_data]
    profit_trend_labels = [datetime.strptime(label, "%Y-%m").strftime("%B") for label in profit_trend_labels]
    profit_trend_values = [data['revenue'] - cost_dict.get(data['month'], 0) for data in monthly_profit_data]

    # --- Category Sales Calculation ---
    all_categories = list(Categories.objects.values_list('categories_name', flat=True))

    # Initialize category_totals (No "Others" category)
    category_totals = {category: 0 for category in all_categories}

    # Get sales data by category
    category_sales = Sales.objects.filter(order__ordered_items__isnull=False).values('order__ordered_items')

    # Process each sale
    for sale in category_sales:
        ordered_items = sale["order__ordered_items"]
        
        for item_name, details in ordered_items.items():
            base_name = "_".join(item_name.split("_")[:-1]) if "_" in item_name else item_name

            item_instance = Inventory.objects.filter(purchase__food_item__icontains=base_name).first()
            category_name = item_instance.category.categories_name if item_instance and item_instance.category else None

            if category_name in category_totals:
                category_totals[category_name] += details["quantity"] * details["price"]
                print(category_name,details["quantity"] * details["price"])

    category_labels = list(category_totals.keys())
    category_values = list(category_totals.values())
    def generate_colors(n):
         return [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(n)]

    category_colors = generate_colors(len(category_labels))


    def generate_bar_colors(n):
        color_palette = ["#F9C784", "#F8B400", "#FF5733", "#36A2EB", "#4BC0C0", 
                        "#9966FF", "#FF6384", "#2ECC71", "#D35400", "#1F618D"]
        return [random.choice(color_palette) for _ in range(n)]

    bar_colors = generate_bar_colors(len(profit_trend_values))


    # --- Final Context Update ---
    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_sales': total_sales,
        'sales_labels': sales_labels,
        'sales_values': sales_values,
        'weekly_sales': weekly_sales,
        'total_profit': total_profit,
        'total_revenue': total_sales,
        'total_cost': total_cost,
        'profit_margin': round((total_profit / total_sales) * 100, 2) if total_sales else 0,
        'profit_trend_labels': profit_trend_labels,
        'profit_trend_values': profit_trend_values,
        'top_items': top_items,
        'category_labels': category_labels,
        'category_values': category_values,
        "category_colors": category_colors,
        "bar_colors": bar_colors,
    }

    return render_page(request, 'adminside/dashboard.html', context)



# Staff View
def staff(request):
    branches = Branch.objects.all()
    staff_members = Staff.objects.all()

    if request.method == 'POST':
        if 'delete_staff_id' in request.POST:
            staff_id = request.POST.get('delete_staff_id')
            staff = get_object_or_404(Staff, staff_id=staff_id)
            staff.delete()
            messages.success(request, f'Staff member "{staff.username}" deleted successfully.')
            return redirect('adminside:staff')

        staff_id = request.POST.get('staff_id')

        form_data = request.POST.copy()  
        form_data['username'] = form_data.get('staff_username')  
        form_data['password'] = form_data.get('staff_password')  

        if staff_id:
            staff = Staff.objects.get(staff_id=staff_id)
            form = StaffForm(form_data, request.FILES, instance=staff)
            message = f'Staff "{staff.username}" updated successfully.'
        else:
            form = StaffForm(form_data, request.FILES)            
            message = 'New staff member added successfully.'


        if form.is_valid():
            print("hello")
            staff = form.save(commit=False)
            staff.save()      
            messages.success(request, message)
            return redirect('adminside:staff')
        else:
            messages.error(request, "Error in form submission. Please check the fields.")
    else:
        form = StaffForm()

    return render_page(request, "adminside/staff.html", {"staff_members": staff_members, "branches": branches, "form": form})

# Branches View
def branches(request):
    branches = Branch.objects.all()
    staff_members = Staff.objects.filter(staff_role="Manager")

    if request.method == 'POST':
        if 'delete_branch_id' in request.POST:
            branch_id = request.POST.get('delete_branch_id')
            if branch_id:
                branch = get_object_or_404(Branch, branch_id=branch_id)
                branch.delete()
                messages.success(request, f'Branch "{branch.location}" deleted successfully.')
                return redirect('adminside:branches')

        branch_id = request.POST.get('branch_id')

        if branch_id:
            try:
                branch = Branch.objects.get(branch_id=int(branch_id))
                form = BranchForm(request.POST, instance=branch)
                message = f'Branch "{branch.location}" updated successfully.'
            except (Branch.DoesNotExist, ValueError):
                return redirect('adminside:branches')
        else:
            form = BranchForm(request.POST)
            message = 'New branch added successfully.'

        if form.is_valid():
            branch = form.save(commit=False)
            manager_id = request.POST.get("manager_id")
            if manager_id:
                branch.manager = Staff.objects.get(staff_id=manager_id)
            else:
                branch.manager = None

            branch.is_active = request.POST.get("is_active") == "True"  
            branch.save()
            messages.success(request, message)
            return redirect('adminside:branches')
        else:
            messages.error(request, "Error in form submission. Please check the fields.")
    else:
        form = StaffForm()

    return render_page(request, "adminside/branches.html", {"branches": branches, "staff_members": staff_members, "form": form})

# Supplier View
def suppliers(request):
    supplier_members= Supplier.objects.all() 

    if request.method == 'POST':
        if 'delete_supplier_id' in request.POST:
            supplier_id = request.POST.get('delete_supplier_id')
            supplier = get_object_or_404(Supplier, supplier_id=supplier_id)
            supplier.delete()
            messages.success(request, f'Supplier "{supplier.supplier_name}" deleted successfully.')
            return redirect('adminside:suppliers')

        supplier_id = request.POST.get('supplier_id')
        print(supplier_id)

        if supplier_id:
            supplier = Supplier.objects.get(supplier_id=supplier_id)
            form = SupplierForm(request.POST, instance=supplier)
            message = f'Supplier "{supplier.supplier_name}" updated successfully.'
        else:
            form = SupplierForm(request.POST)
            message = 'New supplier added successfully.'

        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.save()
            messages.success(request, message)
            return redirect('adminside:suppliers')
        else:
            messages.error(request, "Error in form submission. Please check the fields.")
    else:
        form =SupplierForm()
    return render_page(request, 'adminside/suppliers.html',{"supplier_members":supplier_members,"form":form})

def purchase(request):  
    purchase_items = Purchase.objects.all() 
    suppliers = Supplier.objects.all() 
    branches = Branch.objects.all()
    
    if request.method == 'POST':
        print("POST data received:", request.POST)

        delete_id = request.POST.get('delete_purchase_id')
        if delete_id:
            purchase = get_object_or_404(Purchase, purchase_id=int(delete_id))
            purchase.delete()
            messages.success(request, f"{purchase.food_item} deleted successfully!")
            return redirect('adminside:purchase')

        purchase_id = request.POST.get('purchase_id')

        if purchase_id and purchase_id.isdigit():  
            try:
                purchase = Purchase.objects.get(purchase_id=int(purchase_id))
                form = PurchaseForm(request.POST, instance=purchase)
                message_text = f"{purchase.food_item} updated successfully!"
            except Purchase.DoesNotExist:
                form = PurchaseForm(request.POST)
                message_text = "New purchase added!"  
        else:
            form = PurchaseForm(request.POST) 
            message_text = "New purchase added!" 

        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.save()
            messages.success(request, message_text)
            return redirect('adminside:purchase')
        else:
            messages.error(request, "Error in form submission. Please check the fields.")

    else:
        form = PurchaseForm()
    
    return render_page(request, 'adminside/purchase.html', {
        "purchase_items": purchase_items, 
        "suppliers": suppliers, 
        "branches":branches,
        "form": form
    })

# Categories View
def categories(request):
    categories = Categories.objects.all()

    if request.method == 'POST':
        if 'toggle_category_id' in request.POST:
            category_id = request.POST.get('toggle_category_id')
            category = get_object_or_404(Categories, categories_id=category_id)
            category.status = not category.status  
            category.save()
            messages.success(request, f'Category "{category.categories_name}" status updated.')
            return redirect('adminside:categories')

        if 'delete_category_id' in request.POST:
            category_id = request.POST.get('delete_category_id')
            category = get_object_or_404(Categories, categories_id=category_id)
            category.delete()
            messages.success(request, f'Category "{category.categories_name}" deleted.')
            return redirect('adminside:categories')

        category_id = request.POST.get('category_id')
        if category_id:
            category = get_object_or_404(Categories, categories_id=category_id)
            form = CategoryForm(request.POST, instance=category)
            msg = f'Category "{category.categories_name}" updated successfully.'
        else:
            form = CategoryForm(request.POST)
            msg = 'New category added successfully.'


        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect('adminside:categories')
        else:
            messages.error(request, "Error in form submission. Please check the fields.")

    return render_page(request, 'adminside/categories.html',{"categories":categories,"form":CategoryForm()})

# Inventory View
def inventory(request):
    inventory_items = Inventory.objects.all()
    categories = Categories.objects.all()
    purchase_items = Purchase.objects.all()

    if request.method == "POST":
        if "delete_inventory_id" in request.POST:
            item_id = request.POST.get("delete_inventory_id")
            item = get_object_or_404(Inventory, id=item_id)
            item.delete()
            messages.success(request, f'Inventory item "{item.purchase.food_item}" deleted successfully.')
            return redirect("adminside:inventory")

        item_id = request.POST.get("inventory_id")  
          
        if item_id: 
            item = get_object_or_404(Inventory, id=item_id)
            form = InventoryForm(request.POST, request.FILES, instance=item)
            msg = f'Inventory item "{item.purchase.food_item}" updated successfully.'
        else: 
            form = InventoryForm(request.POST, request.FILES)
            msg = "New inventory item added successfully."

        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect("adminside:inventory")
        else:
            print(form.errors)
            messages.error(request, "Error in form submission. Please check the fields.")

    return render_page(request, 'adminside/inventory.html',{"inventory_items": inventory_items,"categories": categories,"purchase_items":purchase_items,"form":InventoryForm()})

# FoodItem View
def fooditems(request):
    food_items=FoodItem.objects.all()
    return render_page(request, 'adminside/fooditems.html',{"food_items":food_items})

# Tables View
def tables(request):
    tables = Table.objects.all()
    
    if request.method == "POST":
        table_id = request.POST.get("table_id")
        status = request.POST.get("status")
        seats = request.POST.get("seats")

        if table_id:
            # Extract only numeric part (e.g., "T-2" -> "2")
            table_id = "".join(filter(str.isdigit, table_id))

        if table_id and status:
            try:
                table = Table.objects.get(pk=table_id)
                table.status = "vacant" if status == "off" else "reserved"
                table.save()
                messages.success(request, f'Table {table_id} status updated to {table.status}.')
            except Table.DoesNotExist:
                messages.error(request, "Table not found.")

        if seats:
            table = Table.objects.create(seats=int(seats), status="vacant")
            messages.success(request, f'Table with {table.seats} seats added successfully.')

        return redirect("adminside:tables")

    return render_page(request, 'adminside/tables.html', {"tables": tables})
    

# Customer View
def customer(request):
    customers = Customer.objects.all()

    if request.method == 'POST':

        if 'delete_customer_id' in request.POST:  
            customer_id = request.POST.get('delete_customer_id')
            customer = get_object_or_404(Customer, customer_id=customer_id)
            customer.delete()
            messages.success(request, f'Customer "{customer.customer_firstname}" deleted successfully.')
            return redirect('adminside:customer')  

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
            return redirect('adminside:customer')
        else:
            messages.error(request, "Error in form submission. Please check the fields.")

    else:
        form = CustomerForm()
    return render_page(request, 'adminside/customer.html', {"customers": customers, "form": form})

def reports(request):
    filter_type = request.GET.get('filter', 'all')  # Default to "all"

    today = date.today()
    if filter_type == 'today':
        start_date = today
        sales_data = Sales.objects.filter(date=start_date)
    elif filter_type == 'monthly':
        start_date = today.replace(day=1)
        sales_data = Sales.objects.filter(date__gte=start_date)
    elif filter_type == 'yearly':
        start_date = today.replace(month=1, day=1)
        sales_data = Sales.objects.filter(date__gte=start_date)
    else:  
        sales_data = Sales.objects.all()

    sales_data = sales_data.select_related('order__branch')  # ✅ Fix here

    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'quantity': 0, 'image': None})))
    for sale in sales_data:
        sale_date = sale.date.strftime('%Y-%m-%d')
        branch_name = sale.order.branch.location  # ✅ Access branch via order
        order_items = sale.order.ordered_items  
        image_urls = sale.order.image_urls  

        product_images ={}

        for index, (item_name, details) in enumerate(order_items.items()):
            base_name = item_name.rsplit('_', 1)[0]  
            quantity = details['quantity']

            if base_name not in product_images:
                image_url = image_urls[index] if index < len(image_urls) else '/static/images/default.png'
                product_images[base_name] = image_url

            grouped_data[sale_date][branch_name][base_name]['quantity'] += quantity
            grouped_data[sale_date][branch_name][base_name]['image'] = product_images[base_name]

    formatted_data = [
        {
            'date': date,
            'branches': [
                {
                    'branch_name': branch,
                    'products': [
                        {'name': name, 'quantity': details['quantity'], 'image': details['image']}
                        for name, details in items.items()
                    ]
                }
                for branch, items in branches.items()
            ]
        }
        for date, branches in grouped_data.items()
    ]

    return render_page(request, 'adminside/reports.html', {'data': formatted_data, 'filter_type': filter_type})




def sales(request):
    filter_type = request.GET.get('filter', '')  # Get the filter type from request
    today = now().date()

    if filter_type == "today":
        sales_data = Sales.objects.filter(date=today)
    elif filter_type == "monthly":
        sales_data = Sales.objects.filter(date__year=today.year, date__month=today.month)
    elif filter_type == "yearly":
        sales_data = Sales.objects.filter(date__year=today.year)
    else:
        sales_data = Sales.objects.all()  # Show all sales if no filter is applied

    # Prepare data f or template
    sales_list = []
    for sale in sales_data:
        sales_list.append({
            "sales_id": sale.sales_id,
            "order_id": sale.order.order_id if sale.order else "N/A",
            "date": sale.date.strftime("%Y-%m-%d"),
            "time": sale.time.strftime("%H:%M:%S"),
            'branch':sale.order.branch.location,
            "payment_method": sale.payment_method,
            "total_amount": sale.order.final_total if sale.order else 0,
        })

    return render_page(request, 'adminside/sales.html', {'data': sales_list})


# Settings View
def adminside_settings_view(request):
    return redirect('adminside:profile')

def render_settings_page(request, template, context=None):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, template, context or {})
    context = context or {}
    context["template"] = template  # Ensures `template` is still passed
    return render(request, "adminside/settings.html", context)

# Profile View
def profile(request):
    storage = get_messages(request)
    return render_settings_page(request,"adminside/settings/profile.html",{"messages": storage})

# Change Password View
@login_required
def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "✅ Password changed successfully!")
            return redirect("adminside:profile")
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render_settings_page(request, "adminside/settings/change_password.html", {'form': form})

# Update Profile View
@login_required
def update_profile_pic(request):
    if request.method == "POST" and request.FILES.get("profile_pic"):
        staff = request.user 
        staff.staff_img = request.FILES["profile_pic"]
        staff.save()
        messages.success(request, "Profile picture updated successfully!")
        return redirect("adminside:edit_profile")

    messages.error(request, "No file selected. Please try again.")
    return redirect("adminside:edit_profile")  


def edit_profile(request):
    storage = get_messages(request)
    return render_settings_page(request,"adminside/settings/edit_profile.html",{"messages": storage})







