from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum, Q
from pos.models import SaleItem
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProductForm, BarcodePrintForm
from .models import (
    Menu, Country, UISettings, Sale, Product, Purchase, SalesReturn,
    PurchaseReturn, BarcodePrintConfig, Warehouse, TopSellingProduct,
    WeeklySalesData, StockAlert, TopCustomer,SalesTarget, PaymentTransaction,
)
from django.contrib.auth.decorators import login_required
from .models import Customer, Order, OrderItem
from .forms import OrderItemFormSet, CustomerForm
from datetime import timedelta, date
from django.http import HttpResponse
from .utils import update_weekly_data
import datetime
from django.db.models import F
from django.utils import timezone


import json

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('pos:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'pos/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('pos:dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'pos/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('pos:login')


def dashboard(request):
    today = timezone.now().date()
    five_days_ago = today - timedelta(days=4)

    # Core aggregates
    total_sales = Sale.objects.aggregate(total=Sum('total'))['total'] or 0
    total_purchases = Purchase.objects.aggregate(total=Sum('total'))['total'] or 0
    total_sales_returns = SalesReturn.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_purchase_returns = PurchaseReturn.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Stock alerts
    low_stock_products = Product.objects.filter(
        id__in=StockAlert.objects.filter(quantity__lte=F('alert_quantity')).values_list('product_id', flat=True)
    )

    # Top-selling products
    top_products_qs = (
        SaleItem.objects
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:6]
    )
    top_products_labels = [item['product__name'] for item in top_products_qs]
    top_products_data = [item['total_sold'] for item in top_products_qs]

    # Top customers
    top_customers_qs = (
        Sale.objects
        .values('customer__name')
        .annotate(total_spent=Sum('total'))
        .order_by('-total_spent')[:5]
    )
    top_customers_labels = [entry['customer__name'] for entry in top_customers_qs]
    top_customers_data = [float(entry['total_spent']) for entry in top_customers_qs]

    # Weekly data
    weekly_data = WeeklySalesData.objects.all()
    weekly_labels = [entry.day for entry in weekly_data]
    weekly_sales_data = [entry.sales for entry in weekly_data]
    weekly_purchases_data = [entry.purchases for entry in weekly_data]

    # Payments chart data
    payment_labels = [(five_days_ago + timedelta(days=i)).strftime('%a') for i in range(5)]
    payments_sent = []
    payments_received = []
    for i in range(5):
        day = five_days_ago + timedelta(days=i)
        sent = PaymentTransaction.objects.filter(date=day, type='sent').aggregate(Sum('amount'))['amount__sum'] or 0
        received = PaymentTransaction.objects.filter(date=day, type='received').aggregate(Sum('amount'))['amount__sum'] or 0
        payments_sent.append(sent)
        payments_received.append(received)

    # Sales target (static fallback or dynamic)
    sales_target = SalesTarget.objects.last()
    target_data = {
    "weekly": sales_target.weekly if sales_target and sales_target.weekly else 500000,
    "monthly": sales_target.monthly if sales_target and sales_target.monthly else 2000000,
    "yearly": sales_target.yearly if sales_target and sales_target.yearly else 24000000,
}

    # Menus
    menus = Menu.objects.prefetch_related('submenus').all()

    return render(request, 'pos/dashboard.html', {
        "menus": menus,
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "total_sales_returns": total_sales_returns,
        "total_purchase_returns": total_purchase_returns,
        "low_stock_products": low_stock_products,
        "top_products_labels": json.dumps(top_products_labels),
        "top_products_data": json.dumps(top_products_data),
        "weekly_labels": json.dumps(weekly_labels),
        "weekly_sales_data": json.dumps(weekly_sales_data),
        "weekly_purchases_data": json.dumps(weekly_purchases_data),
        "top_customers_labels": json.dumps(top_customers_labels),
        "top_customers_data": json.dumps(top_customers_data),
        "sales_target": json.dumps(target_data),
        "payment_labels": json.dumps(payment_labels),
        "payments_sent": json.dumps(payments_sent),
        "payments_received": json.dumps(payments_received),
    })


def dashboard_view(request):
    menus = Menu.objects.prefetch_related('submenus').all()
    countries = Country.objects.all()
    return render(request, 'dashboard.html', {'countries': countries, 'menus': menus})

def some_view(request):
    ui_settings = UISettings.objects.first()
    return render(request, 'your_template.html', {
        'ui_settings': ui_settings,
    })

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('pos:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'pos/signup.html', {'form': form})

def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # adjust to your URL name
    else:
        form = ProductForm()
    return render(request, 'create_product.html', {'form': form})

def product_success(request):
    return render(request, 'products/success.html')

def product_list_view(request):
    products = Product.objects.all()
    categories = Product.objects.values_list('category', flat=True).distinct()
    brands = Product.objects.values_list('brand', flat=True).distinct()
    menus = Menu.objects.prefetch_related('submenus')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()

    search = request.GET.get('search')
    category = request.GET.get('category')
    brand = request.GET.get('brand')

    if search:
        products = products.filter(Q(name__icontains=search) | Q(product_code__icontains=search))
    if category:
        products = products.filter(category=category)
    if brand:
        products = products.filter(brand=brand)

    context = {
        'form': form,
        'products': products,
        'categories': categories,
        'brands': brands,
        'menus': menus,
    }
    return render(request, 'pos/product_list.html', context)

def export_products_excel(request):
    return HttpResponse("Excel export not yet implemented.", content_type="text/plain")

def export_products_pdf(request):
    return HttpResponse("PDF export not yet implemented.", content_type="text/plain")

def print_barcode_view(request):
    products = Product.objects.all()
    menus = Menu.objects.prefetch_related('submenus').all()

    if request.method == 'POST':
        form = BarcodePrintForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pos:print_barcode')  # reload after save
    else:
        form = BarcodePrintForm()

    return render(request, 'pos/print_barcode.html', {
        'menus': menus,
        'form': form,
    })

def create_sale(request):
    if request.method == 'POST':
        # Create a basic Sale record (customize this with your own form and logic)
        total = float(request.POST.get('total', 0))  # or calculate based on items
        sale = Sale.objects.create(total=total)
        update_weekly_data('sale', sale.total)
        return redirect('pos:dashboard')
    return HttpResponse("Sale form not implemented.")

def create_purchase(request):
    if request.method == 'POST':
        total = float(request.POST.get('total', 0))
        purchase = Purchase.objects.create(total=total)
        update_weekly_data('purchase', purchase.total)
        return redirect('pos:dashboard')
    return HttpResponse("Purchase form not implemented.")

def product_cards(request):
    products = Product.objects.all()
    return render(request, 'product_cards.html', {'products': products})


@login_required
def create_order(request):
    customer, _ = Customer.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        cust_form = CustomerForm(request.POST, instance=customer)
        formset = OrderItemFormSet(request.POST)
        if cust_form.is_valid() and formset.is_valid():
            cust_form.save()
            order = Order.objects.create(customer=customer)
            items = formset.save(commit=False)
            for item in items:
                item.order = order
                item.unit_price = item.product.price
                item.save()
            return redirect('order_summary', order_id=order.id)
    else:
        cust_form = CustomerForm(instance=customer)
        formset = OrderItemFormSet()
    return render(request, 'orders/create_order.html', {
        'cust_form': cust_form,
        'formset': formset,
    })

@login_required
def order_summary(request, order_id):
    order = Order.objects.get(id=order_id, customer__user=request.user)
    return render(request, 'orders/order_summary.html', {'order': order})

