from django.contrib import admin
from .models import Inventory,Branch,Purchase,Table,Sales_reports,Supplier,Categories,Customer,Staff

admin.site.register(Table)

# Register your models here.
class BranchAdmin(admin.ModelAdmin):
  list_display = ("branch_id", "location", "area","manager_id","phone_no","is_active")
admin.site.register(Branch, BranchAdmin)


class PurchaseAdmin(admin.ModelAdmin):
  list_display = ("food_item_id", "food_item", "cost_price","supplier_id","purchased_date","payment_status")
admin.site.register(Purchase, PurchaseAdmin)

class InventoryAdmin(admin.ModelAdmin):
  list_display = ("food_item_id", "image", "food_item_name","category","description","quantity","branch","sell_price","cost_price","mfg_date","exp_date")
admin.site.register(Inventory, InventoryAdmin)


class SalesAdmin(admin.ModelAdmin):
    list_display=("product_id","product_name","categories","quantities")
admin.site.register(Sales_reports,SalesAdmin)

class SupplierAdmin(admin.ModelAdmin):
    list_display=("supplier_id","supplier_name","company_name","supplier_email","supplier_phone","address","branch")
admin.site.register(Supplier,SupplierAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display=("categories_id","categories_name","status")
admin.site.register(Categories,CategoryAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display=("customer_id","customer_firstname","customer_lastname","customer_email","customer_phone","gender")
admin.site.register(Customer,CustomerAdmin)


from django.contrib import admin # type: ignore 
from django import forms # type: ignore 
from django.contrib.auth.hashers import make_password # type: ignore 

class StaffAdminForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'

    def clean_staff_password(self):
        password = self.cleaned_data.get("staff_password")

        if self.instance and self.instance.pk:
            existing_staff = Staff.objects.get(pk=self.instance.pk)
            if existing_staff.staff_password == password:  
                return password 
        
        if not password.startswith("pbkdf2_sha256$"):
            return make_password(password)
        return password

class StaffAdmin(admin.ModelAdmin):
    form = StaffAdminForm
    list_display = [field.name for field in Staff._meta.fields] 

admin.site.register(Staff, StaffAdmin)


