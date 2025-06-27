from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'code', 'category', 'brand', 'barcode_symbology', 'product_cost', 'price', 'product_unit', 'sales_unit', 'purchase_unit', 'quantity', 'order_tax', 'tax_type', 'notes', 'image']

