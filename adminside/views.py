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
import re
import csv
from django.http import JsonResponse # type: ignore
from datetime import date
from django.db.models import F, Sum # type: ignore



def render_page(request, template, data=None):
    today = timezone.now().date()

    context = {
        "template": template,
        "user": request.user,
        "login_date": request.session.get("login_date"),
        "open_notifications": request.GET.get("open_notifications") == "true"
    }

    if request.user.is_authenticated:
        all_notifications = Notification.objects.filter(created_at__date=today).order_by("-created_at")

        unseen_notifications = all_notifications.exclude(
            notificationseen__user=request.user,
            notificationseen__seen=True
        )

        context["notifications"] = all_notifications
        context["has_unseen"] = unseen_notifications.exists()
        context["unseen_notifications"] = unseen_notifications 

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

# Dashboard View
def dashboard(request):
    total_orders = Order.objects.count()

    total_customers = Customer.objects.count()

    total_sales = Sales.objects.aggregate(total=Sum('order__final_total'))['total'] or 0

    total_cost = Purchase.objects.aggregate(total_cost=Sum(F('cost_price') * F('quantity')))['total_cost'] or 0
    total_profit = total_sales - total_cost


    
    last_week = datetime.today() - timedelta(days=7)
    weekly_sales = (
        Sales.objects.filter(date__gte=last_week)
        .aggregate(total=Sum('order__final_total'))['total'] or 0
    )

    today = datetime.today()
    last_week = today - timedelta(days=7)
    sales_data = (
        Sales.objects
        .filter(date__gte=last_week) 
        .values('date')
        .annotate(total=Sum('order__final_total'))
        .order_by('date')
    )

    sales_labels = [data['date'].strftime('%Y-%m-%d') for data in sales_data]
    sales_values = [data['total'] for data in sales_data]

    best_selling_items = Order.objects.values_list('ordered_items', flat=True)
    item_count = defaultdict(lambda: {"quantity": 0, "total_price": 0, "image": "", "price": 0})

    for items in best_selling_items:
        for item_name, details in items.items():
            base_name = item_name.split('_')[0]  

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

    monthly_profit_data = (
        Sales.objects.annotate(month=TruncMonth('date'))  
        .values('month')
        .annotate(revenue=Sum('order__final_total'))
        .order_by('month')
    )

    monthly_cost_data = (
        Purchase.objects.annotate(month=TruncMonth('purchased_date'))
        .values('month')
        .annotate(cost=Sum('cost_price'))
        .order_by('month')
    )

    cost_dict = {data['month']: data['cost'] for data in monthly_cost_data}

    profit_trend_labels = [data['month'].strftime('%Y-%m') for data in monthly_profit_data]
    profit_trend_labels = [datetime.strptime(label, "%Y-%m").strftime("%B") for label in profit_trend_labels]
    profit_trend_values = [data['revenue'] - cost_dict.get(data['month'], 0) for data in monthly_profit_data]

    all_categories = list(Categories.objects.values_list('categories_name', flat=True))

    category_totals = {category: 0 for category in all_categories}

    category_sales = Sales.objects.filter(order__ordered_items__isnull=False).values('order__ordered_items')

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
        if 'csv_file' in request.FILES:  # Handle CSV Upload
            csv_file = request.FILES['csv_file']
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Invalid file format. Please upload a CSV file.")
                return redirect('adminside:purchase')

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for row in reader:
                    row = {key.strip(): value.strip() for key, value in row.items() if key.strip()}  # Remove empty column keys


                    if not any(row.values()):  # Ignore completely empty rows
                        continue

                    supplier_data = row['Supplier'].split(' - ') 
                    supplier_name = supplier_data[0].strip() 
                    company_name = supplier_data[1].strip() if len(supplier_data) > 1 else None  

                    supplier = Supplier.objects.filter(supplier_name__iexact=supplier_name, company_name__iexact=company_name).first()

                    # Extract location and area from CSV
                    csv_value = row['Branch'].strip()  
                    csv_value = re.sub(r'\s*-\s*', ' - ', csv_value)  

                    if " - " in csv_value:
                        csv_location, csv_area = csv_value.split(" - ", 1)
                    else:
                        csv_location = csv_value
                        csv_area = None

                    branch = Branch.objects.filter(location__iexact=csv_location, area__iexact=csv_area).first()

                    if supplier and branch:
                        Purchase.objects.create(
                            food_item=row['Food Item'],
                            quantity=int(row['Quantity']),
                            cost_price=float(row['Cost Price']),
                            supplier=supplier,
                            branch=branch,
                            purchased_date=row['Purchase Date'],
                            payment_status=row['Payment Status']
                        )
                        messages.success(request, f"CSV added successfully ")
                    else:
                        print("Invalid Row:", row)  # Debugging
                        messages.error(request, f"Invalid supplier or branch in CSV row: {row}")
                        return redirect('adminside:purchase')

            except Exception as e:
                print(e)
                messages.error(request, f"Error processing CSV file: {str(e)}")
            
            return redirect('adminside:purchase')

        # Handle purchase deletion
        delete_id = request.POST.get('delete_purchase_id')
        if delete_id:
            purchase = get_object_or_404(Purchase, purchase_id=int(delete_id))
            purchase.delete()
            messages.success(request, f"{purchase.food_item} deleted successfully!")
            return redirect('adminside:purchase')

        # Handle purchase form submission
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
        "branches": branches,
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

from django.core.files.storage import default_storage # type: ignore
from django.core.files.base import ContentFile # type: ignore


def inventory(request):
    inventory_items = Inventory.objects.all()
    categories = Categories.objects.all()
    purchase_items = Purchase.objects.all()

    if request.method == "POST":
        if "delete_inventory_id" in request.POST:
            item_id = request.POST.get("delete_inventory_id")
            item = get_object_or_404(Inventory, id=item_id)
            food_item_name = item.purchase.food_item
            branch = item.purchase.branch
            item.delete()
            
            remaining_inventory = Inventory.objects.filter(purchase__food_item=food_item_name, purchase__branch=branch).count()
            
            if remaining_inventory == 0:
                FoodItem.objects.filter(name=food_item_name, branch=branch).delete()

            messages.success(request, f'Inventory item "{item.purchase.food_item}" deleted successfully.')
            return redirect("adminside:inventory")

        if "csv_file" in request.FILES:
            csv_file = request.FILES["csv_file"]
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Only CSV files are allowed.")
                return redirect("adminside:inventory")

            file_path = default_storage.save(f"uploads/{csv_file.name}", ContentFile(csv_file.read()))
            with open(default_storage.path(file_path), 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip header row

                for row in csv_reader:
                    try:
                        purchase = Purchase.objects.get(purchase_id=row[0]) 
                        category = Categories.objects.get(categories_id=row[1])  
                        description = row[2]
                        price = int(row[3])
                        cost = int(row[4])
                        mfg_date = row[5]
                        exp_date = row[6]
                        active = row[7].strip().lower() == "true"

                        Inventory.objects.create(
                            purchase=purchase,
                            category=category,
                            description=description,
                            price=price,
                            cost=cost,
                            mfg_date=mfg_date,
                            exp_date=exp_date,
                            active=active,
                        )
                    except Exception as e:
                        price(e)
                        messages.error(request, f"Error processing row: {row} - {str(e)}")

            messages.success(request, "CSV file uploaded successfully.")
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

    return render_page(request, 'adminside/inventory.html', {
        "inventory_items": inventory_items,
        "categories": categories,
        "purchase_items": purchase_items,
        "form": InventoryForm()
    })


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




from datetime import date  # ✅ Required import

from collections import defaultdict
import re
from datetime import date

def reports(request):
    filter_type = request.GET.get('filter', 'all')
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

    sales_data = sales_data.select_related('order__branch')

    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for sale in sales_data:
        sale_date = sale.date.strftime('%Y-%m-%d')
        branch_name = f"{sale.order.branch.location} - {sale.order.branch.area}"

        for item_name, details in sale.order.ordered_items.items():
            if isinstance(details, dict):
                quantity = details.get('quantity', 0)
            elif isinstance(details, list):
                quantity = details[0].get('quantity', 0) if details and isinstance(details[0], dict) else 0
            else:
                quantity = 0  

            clean_name = re.sub(r'_(small|medium|large)$', '', item_name)  

            if clean_name in grouped_data[sale_date][branch_name]:
                grouped_data[sale_date][branch_name][clean_name] += quantity 
            else:
                grouped_data[sale_date][branch_name][clean_name] = quantity 

    formatted_data = []
    for report_date, branches in grouped_data.items():
        branch_list = []

        for branch, products in branches.items():
            product_list = [{'name': name, 'quantity': quantity} for name, quantity in products.items()]
            
            branch_list.append({
                'branch_name': branch,
                'products': product_list,
                'product_count': len(product_list)  # ✅ Calculate count here
            })

        formatted_data.append({
            'date': report_date,
            'branches': branch_list,
            'date_rowspan': sum(branch['product_count'] for branch in branch_list)  # ✅ Fix applied here
        })

    return render_page(request, 'adminside/reports.html', {'data': formatted_data, 'filter_type': filter_type})





def sales(request):
    filter_type = request.GET.get('filter', '') 
    today = now().date()

    if filter_type == "today":
        sales_data = Sales.objects.filter(date=today)
    elif filter_type == "monthly":
        sales_data = Sales.objects.filter(date__year=today.year, date__month=today.month)
    elif filter_type == "yearly":
        sales_data = Sales.objects.filter(date__year=today.year)
    else:
        sales_data = Sales.objects.all()  

    sales_list = []
    for sale in sales_data:
        sales_list.append({
            "sales_id": sale.sales_id,
            "order_id": sale.order.order_id if sale.order else "N/A",
            "date": sale.date.strftime("%Y-%m-%d"),
            "time": sale.time.strftime("%H:%M:%S"),
            'branch':f'{sale.order.branch.location} - {sale.order.branch.area}',
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
    context["template"] = template
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







