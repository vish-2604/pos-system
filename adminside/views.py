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

    return render(request, "adminside/base.html", context)

# Home View
def home(request):
    messages.success(request, "✅ Login successful!")  
    return redirect("adminside:dashboard")

# Dashboard View
def dashboard(request):
    return render_page(request, 'adminside/dashboard.html')

# Staff View
def staff(request):
    branches = Branch.objects.all()
    staff_members = Staff.objects.all()

    if request.method == 'POST':
        if 'delete_staff_id' in request.POST:
            staff_id = request.POST.get('delete_staff_id')
            staff = get_object_or_404(Staff, staff_id=staff_id)
            staff.delete()
            messages.success(request, f'Staff member "{staff.staff_name}" deleted successfully.')
            return redirect('adminside:staff')

        staff_id = request.POST.get('staff_id')

        form_data = request.POST.copy()  
        form_data['username'] = form_data.get('staff_username')  
        form_data['password'] = form_data.get('staff_password')  

        if staff_id:
            staff = Staff.objects.get(staff_id=staff_id)
            form = StaffForm(form_data, request.FILES, instance=staff)
            message = f'Staff "{staff.staff_name}" updated successfully.'
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

# Purchase View
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
        print(request.POST)
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
            messages.error(request, "Error in form submission. Please check the fields.")

    return render_page(request, 'adminside/inventory.html',{"inventory_items": inventory_items,"categories": categories,"purchase_items":purchase_items,"form":InventoryForm()})

# FoodItem View
def fooditems(request):
    food_items=FoodItem.objects.all()
    return render_page(request, 'adminside/fooditems.html',{"food_items":food_items})

# Tables View
def tables(request):
    tables=Table.objects.all()
    if request.method == "POST":
        seats = request.POST.get("seats")  # Get seat value from form
        if seats:
            table=Table.objects.create(seats=int(seats), status="vacant")
            messages.success(request, f'Table with {table.seats} seats added successfully.')  
        return redirect("adminside:tables")

    return render_page(request, 'adminside/tables.html',{"tables":tables})

# Customer View
def customer(request):
    customers = Customer.objects.all()

    if request.method == 'POST':
        print("Received POST request with data:", request.POST) 

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

# Reports View
def reports(request):
    sales_reports=Sales_reports.objects.all()
    return render_page(request, 'adminside/reports.html',{"sales_reports":sales_reports})

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







