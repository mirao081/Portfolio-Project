from django.db import models
from django.db.models import F
from django.conf import settings
from django.utils import timezone
from inventory.models import Product
from django.contrib.auth.models import AbstractUser


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name

# models.py

class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Return/exchange fields
    is_returned = models.BooleanField(default=False)
    is_exchange = models.BooleanField(default=False)
    exchange_for = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='exchanges'
    )

    def __str__(self):
        return f"Sale #{self.id}"

    def update_total(self):
        self.total = sum(item.subtotal for item in self.items.all())
        self.save()


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
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']

class SubMenu(models.Model):
    menu = models.ForeignKey(Menu, related_name='submenus', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.menu.name} → {self.name}"



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
    

    
class TopCustomer(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customer} - ₦{self.total_spent}"
    

class SalesTarget(models.Model):
    daily = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    weekly = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    yearly = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Targets - Daily: {self.daily}, Monthly: {self.monthly}"
    
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
    
class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    show_to_salesperson = models.BooleanField(default=True)

    def __str__(self):
        return self.message[:50]
    

    
class Discount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.percentage}% off {self.product.name}"

    class Meta:
        permissions = [
            ("can_apply_discount", "Can apply discount to products"),
        ]

class Receipt(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)

class SalesReturn(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return of ₦{self.amount} from {self.sale}"

# pos/models.py
class StockAlert(models.Model):
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE, related_name='pos_stock_alerts')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    alert_quantity = models.PositiveIntegerField(default=10)
    alert_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Stock alert for {self.product.name}"

class Return(models.Model):
    sale_item = models.ForeignKey(SaleItem, on_delete=models.CASCADE)
    reason = models.TextField()
    date = models.DateTimeField(auto_now_add=True)