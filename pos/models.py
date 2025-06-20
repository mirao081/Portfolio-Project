from django.db import models
from django.db.models import F
from inventory.models import Product
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name

class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Sale #{self.id}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Payment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile', 'Mobile'),
        ('other', 'Other')
    ])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Sale #{self.sale.id}"
    

class Menu(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class SubMenu(models.Model):
    menu = models.ForeignKey(Menu, related_name='submenus', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    icon = models.ImageField(upload_to='submenu_icons/', blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.menu.name} → {self.name}"


class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    role = models.CharField(max_length=50, choices=[('sales_rep', 'Sales Rep'), ('supervisor', 'Supervisor'), ('admin', 'Admin/GM')])

class UISettings(models.Model):
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return "UI Settings"

    class Meta:
        verbose_name = "UI Setting"
        verbose_name_plural = "UI Settings"

# List of available countries
class Country(models.Model):
    name = models.CharField(max_length=100)
    flag = models.ImageField(upload_to='flags/', blank=True, null=True)

    def __str__(self):
        return self.name
    

CATEGORY_CHOICES = [
    ('Phones', 'Phones'),
    ('Wristwatches', 'Wristwatches'),
    ('Computer Accessories', 'Computer Accessories'),
]

BRAND_CHOICES = [
    ('Brand One', 'Brand One'),
    ('Brand Two', 'Brand Two'),
]

AVAILABILITY_CHOICES = [
    ('In Stock', 'In Stock'),
    ('Out of Stock', 'Out of Stock'),
]

UNIT_CHOICES = [
    (5, '5'),
    (10, '10'),
    (15, '15'),
]

TAX_CHOICES = [
    ('inclusive', 'Inclusive'),
    ('exclusive', 'Exclusive'),
]

class Product(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    barcode_symbology = models.CharField(max_length=255)
    product_cost = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_unit = models.IntegerField(choices=UNIT_CHOICES)
    sales_unit = models.IntegerField(choices=UNIT_CHOICES)
    purchase_unit = models.IntegerField(choices=UNIT_CHOICES)
    quantity = models.IntegerField()

    order_tax = models.PositiveIntegerField(help_text="Percentage (%)")
    tax_type = models.CharField(max_length=20, choices=TAX_CHOICES)
    notes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class BarcodeSettings(models.Model):
    label = models.CharField(max_length=100, default="Product Barcode")
    width = models.IntegerField(default=400)
    height = models.IntegerField(default=100)
    font_size = models.IntegerField(default=10)

    def __str__(self):
        return self.label
    

class Warehouse(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BarcodePrintConfig(models.Model):
    selected_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    product_code = models.CharField(max_length=100, blank=True, help_text="Scan or search by code")

    def __str__(self):
        return f"Barcode Print Config"
    
class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

class SalesReturn(models.Model):
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

class PurchaseReturn(models.Model):
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

class TopSellingProduct(models.Model):
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()

    def __str__(self):
        return self.product

class WeeklySalesData(models.Model):
    day = models.CharField(max_length=10)
    sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.day
    
class StockAlert(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    warehouse = models.CharField(max_length=100)
    quantity = models.IntegerField()
    alert_quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - Alert at {self.alert_quantity}"   
    
class TopCustomer(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customer} - ₦{self.total_spent}"
    

class SalesTarget(models.Model):
    weekly = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    yearly = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Sales Targets - Weekly: {self.weekly}, Monthly: {self.monthly}, Yearly: {self.yearly}"

class PaymentTransaction(models.Model):
    date = models.DateField(default=timezone.now)
    type = models.CharField(max_length=10, choices=[('sent', 'Sent'), ('received', 'Received')])
    amount = models.DecimalField(max_digits=12, decimal_places=2)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [('pending','Pending'),('confirmed','Confirmed'),('shipped','Shipped')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    def total_amount(self):
        return sum(item.quantity * item.unit_price for item in self.items.all())
    def __str__(self):
        return f"Order #{self.id} by {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    def subtotal(self):
        return self.quantity * self.unit_price
    def __str__(self):
        return f"{self.quantity}×{self.product.name}"