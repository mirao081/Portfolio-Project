from django.contrib import admin
from .models import Menu, SubMenu, CustomUser, UISettings, Country
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Product
from .models import Warehouse, BarcodePrintConfig,TopSellingProduct, WeeklySalesData
from .models import StockAlert, TopCustomer,Customer,SalesTarget, PaymentTransaction


# --- Submenu Inline Admin ---
class SubMenuInline(admin.TabularInline):
    model = SubMenu
    extra = 1

# --- Menu Admin ---
class MenuAdmin(admin.ModelAdmin):
    inlines = [SubMenuInline]

# --- Custom User Admin with Profile Image Preview ---
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'profile_image_tag')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'profile_image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('role', 'profile_image')}),
    )

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="30" height="30" style="object-fit: cover; border-radius: 50%;" />',
                obj.profile_image.url
            )
        return "-"
    profile_image_tag.short_description = 'Profile Image'

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'flag_preview')

    def flag_preview(self, obj):
        if obj.flag:
            return format_html('<img src="{}" style="height: 20px; width: auto;" />', obj.flag.url)
        return "-"
    flag_preview.short_description = 'Flag'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'brand', 'price')
    list_editable = ('price',)  # Makes these editable from list view
    list_filter = ('category', 'brand')
    search_fields = ('name', 'code', 'brand')

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(BarcodePrintConfig)
class BarcodePrintConfigAdmin(admin.ModelAdmin):
    list_display = ['selected_warehouse', 'product_code']

@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity', 'alert_quantity')
    search_fields = ('product__name', 'warehouse')

@admin.register(TopCustomer)
class TopCustomerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'total_spent')
    search_fields = ('customer__name',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')

# --- Admin Registrations ---
admin.site.register(Menu, MenuAdmin)
admin.site.register(CustomUser, CustomUserAdmin)  # ✅ Use your customized admin
admin.site.register(UISettings)
from .models import BarcodeSettings
admin.site.register(BarcodeSettings)
admin.site.register(TopSellingProduct)
admin.site.register(WeeklySalesData)
admin.site.register(SalesTarget)
admin.site.register(PaymentTransaction)



# Register your models here.
