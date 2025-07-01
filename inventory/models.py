import uuid
from django.db import models
import os
from io import BytesIO
from django.core.files import File
import barcode
from barcode.writer import ImageWriter
from django.conf import settings


TAX_CHOICES = [
    ('inclusive', 'Inclusive'),
    ('exclusive', 'Exclusive'),
]

CATEGORY_CHOICES = [
    ('Phones', 'Phones'),
    ('Wristwatches', 'Wristwatches'),
    ('Computer Accessories', 'Computer Accessories'),
]

BRAND_CHOICES = [
    ('Apple', 'Apple'),
    ('Samsung', 'Samsung'),
    ('Microsoft', 'Microsoft'),
]

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    barcode_symbology = models.CharField(max_length=255)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    product_cost = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_unit = models.IntegerField(default=1)
    sales_unit = models.IntegerField(default=1)
    purchase_unit = models.IntegerField(default=1)
    quantity = models.IntegerField()

    order_tax = models.PositiveIntegerField(help_text="Percentage (%)")
    tax_type = models.CharField(max_length=20, choices=TAX_CHOICES)
    notes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to get an ID if needed

        if self.barcode_symbology:
            barcode_class = barcode.get_barcode_class('code128')  # or use 'ean13', etc.
            code = barcode_class(self.barcode_symbology, writer=ImageWriter())

            buffer = BytesIO()
            code.write(buffer)
            filename = f"{self.code}_barcode.png"

            self.barcode_image.save(filename, File(buffer), save=False)
            buffer.close()

            super().save(update_fields=['barcode_image']) 


# inventory/models.py
class StockAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_stock_alerts')
    warehouse = models.CharField(max_length=100)
    quantity = models.IntegerField()
    alert_quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - Alert at {self.alert_quantity}"

