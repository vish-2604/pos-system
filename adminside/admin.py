from django.contrib import admin # type: ignore
from .models import Inventory,Branch,Purchase,Table,Sales_reports,Supplier,Categories,Customer,Staff,FoodItem
from django import forms  # type: ignore
from django.contrib.auth.hashers import make_password   # type: ignore
from adminside.models import Staff # type: ignore

admin.site.register(Table)

class BranchAdmin(admin.ModelAdmin):
  list_display = ("branch_id", "location", "area","manager_id","phone_no","is_active")
admin.site.register(Branch, BranchAdmin)

class SupplierAdmin(admin.ModelAdmin):
    list_display=("supplier_id","supplier_name","company_name","supplier_email","address","supplier_phone")
admin.site.register(Supplier,SupplierAdmin)

class PurchaseAdmin(admin.ModelAdmin):
  list_display = ("purchase_id", "food_item", "cost_price","supplier","branch","purchased_date","payment_status")
admin.site.register(Purchase, PurchaseAdmin)

class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "id", "image", "purchase", "category", "description", "price", "cost",
        "mfg_date", "exp_date","quantity"
    )
admin.site.register(Inventory, InventoryAdmin)

class FoodItemAdmin(admin.ModelAdmin):
    list_display = ("id","image", "name","category" , "price", "description", "quantity",'branch',"is_special")
admin.site.register(FoodItem, FoodItemAdmin)


class SalesAdmin(admin.ModelAdmin):
    list_display=("id","name","category","quantity_sold","total_price","sold_date")
admin.site.register(Sales_reports,SalesAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display=("categories_id","categories_name","status")
admin.site.register(Categories,CategoryAdmin)

class CustomerAdmin(admin.ModelAdmin):
    list_display=("customer_id","customer_firstname","customer_lastname","customer_email","customer_phone","gender")
admin.site.register(Customer,CustomerAdmin)

class StaffAdminForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'  

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if self.instance and self.instance.pk:
            if self.instance.password == password: 
                return password  

        if not password.startswith("pbkdf2_sha256$"):
            return make_password(password)

        return password



