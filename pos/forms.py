from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import CustomUser
from .models import Product
from .models import BarcodePrintConfig
from .models import Order, OrderItem, Customer,Discount, Sale

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'code', 'price', 'quantity', 'brand', 'category', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BarcodePrintForm(forms.ModelForm):
    class Meta:
        model = BarcodePrintConfig
        fields = ['selected_warehouse', 'product_code']
        widgets = {
            'selected_warehouse': forms.Select(attrs={'class': 'form-control'}),
            'product_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Scan/search product by code'
            }),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')

OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class NewSaleForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class ReturnExchangeForm(forms.Form):
    sale = forms.ModelChoiceField(queryset=Sale.objects.all())
    return_type = forms.ChoiceField(choices=[('return', 'Return'), ('exchange', 'Exchange')])
    new_product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False)

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['product', 'percentage']

class ReceiptForm(forms.Form):
    sale = forms.ModelChoiceField(queryset=Sale.objects.all())