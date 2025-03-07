from django.shortcuts import render, redirect, get_object_or_404  # type: ignore
from .forms import CustomPasswordChangeForm
from adminside.models import Table
from django.db import connection # type: ignore
from .models import Staff,Branch
from .forms import StaffForm,BranchForm
from django.contrib import messages # type: ignore
from django.utils import timezone # type: ignore

def home(request):
    return redirect('adminside:dashboard')

def render_page(request, template, data=None):
    context = {
        "template": template,
        "user": request.user, 
        "login_date": request.session.get('login_date'),
    }

    if request.user.is_authenticated:
        print(request.user.staff_username) 
    else:
        print("User is not authenticated")

    if data:
        context.update(data)
    return render(request, "adminside/base.html", context)


def staff(request):
    branches = Branch.objects.all() 
    staff_members = Staff.objects.all()

    if request.method == 'POST':
        if 'delete_staff_id' in request.POST:  # Check if delete request is made
            staff_id = request.POST.get('delete_staff_id')
            staff = get_object_or_404(Staff, staff_id=staff_id)
            staff.delete()
            messages.success(request, "Staff member deleted successfully.")
            return redirect('adminside:staff')

        staff_id = request.POST.get('staff_id')

        if staff_id:
            staff = Staff.objects.get(staff_id=staff_id)
            form = StaffForm(request.POST, request.FILES, instance=staff)
        else:
            form = StaffForm(request.POST, request.FILES)

        if form.is_valid():
            staff = form.save(commit=False)
            staff.is_active = request.POST.get("is_active") == "True"  # Convert to Boolean
            staff.date_joined = request.POST.get("date_joined") or timezone.now().date()
            staff.save()

            return redirect('adminside:staff')
        else:
            print(form.errors)

    else:
        form = StaffForm()

    return render_page(request, "adminside/staff.html", {"staff_members": staff_members, "branches": branches,"form": form,})

def branches(request):
    branches = Branch.objects.all()
    staff_members = Staff.objects.filter(staff_role="Manager")

    if request.method == 'POST':
        if 'delete_branch_id' in request.POST:
            branch_id = request.POST.get('delete_branch_id')
            if branch_id:
                branch = get_object_or_404(Branch, branch_id=branch_id)
                branch.delete()
                messages.success(request, "Branch deleted successfully.")
                return redirect('adminside:branches')

        branch_id = request.POST.get('branch_id')

        if branch_id:
            try:
                branch = Branch.objects.get(branch_id=int(branch_id))
                form = BranchForm(request.POST, instance=branch)
            except (Branch.DoesNotExist, ValueError):
                messages.error(request, "Invalid branch ID.")
                return redirect('adminside:branches')
        else:
            form = BranchForm(request.POST)

        if form.is_valid():
            branch = form.save(commit=False)
            manager_id = request.POST.get("manager_id")
            if manager_id:
                branch.manager = Staff.objects.get(staff_id=manager_id)
            else:
                branch.manager = None

            branch.is_active = request.POST.get("is_active") == "True"  
            branch.save()
            messages.success(request, "Branch updated successfully." if branch_id else "Branch added successfully.")
            return redirect('adminside:branches')
        else:
            print(form.errors)
    else:
        form = StaffForm()

    return render_page(request, "adminside/branches.html", {"branches": branches, "staff_members": staff_members, "form": form})

def dashboard(request):
    return render_page(request, 'adminside/dashboard.html')

def suppliers(request):
    return render_page(request, 'adminside/suppliers.html')

def purchase(request):    
    return render_page(request, 'adminside/purchase.html')

def categories(request):
    return render_page(request, 'adminside/categories.html')

def inventory(request):
    return render_page(request, 'adminside/inventory.html')

def fooditems(request):
    return render_page(request, 'adminside/fooditems.html')

def tables(request):
    return render_page(request, 'adminside/tables.html')

def customer(request):
    return render_page(request, 'adminside/customer.html')

def reports(request):
    sales_data = [
    {"product_id": "101", "product_name": "Neapolitan Pizaa", "calegories": "Pizaa", "email": "john.doe@example.com", "quentity": "450", "paid": "200", "balance": "250", "date": "01/15"},
    {"product_id": "102", "product_name": "Veg. Burger", "calegories": "Burger", "email": "jane.smith@example.com", "quentity": "350", "paid": "150", "balance": "200", "date": "01/16"},
    {"product_id": "103", "product_name": "French Fries", "calegories": "Fast Food", "email": "robert.brown@example.com", "quentity": "500", "paid": "250", "balance": "250", "date": "01/17"},
    {"product_id": "104", "product_name": "Veg. Sandvich", "calegories": "Sandvich", "email": "emily.white@example.com", "quentity": "600", "paid": "300", "balance": "300", "date": "01/18"},
    {"product_id": "105", "product_name": "Dosa (Butter)", "calegories": "South Indian", "email": "michael.green@example.com", "quentity": "750", "paid": "500", "balance": "250", "date": "01/19"},
    ]
    return render_page(request, 'adminside/reports.html', data=sales_data)


def adminside_settings_view(request):
    return redirect('adminside:profile')

def render_settings_page(request, template, context=None):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, template, context or {})
    context = context or {}
    context["template"] = template  # Ensures `template` is still passed
    return render(request, "adminside/settings.html", context)

def change_password(request):
    form = CustomPasswordChangeForm(request.user)
    return render_settings_page(request, "adminside/settings/change_password.html", {'form': form})

def edit_profile(request):
    return render_settings_page(request,"adminside/settings/edit_profile.html")

def profile(request):
    return render_settings_page(request,"adminside/settings/profile.html")

def logout_view(request):
    sales_data = [
    {"invoice_no": "101", "full_name": "John Doe", "phone": "9876543210", "email": "john.doe@example.com", "total": "450", "paid": "200", "balance": "250", "date": "01/15"},
    
    ]
    return render_page(request, 'adminside/logout.html',data=sales_data)







