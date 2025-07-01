from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required,permission_required,user_passes_test

from django.db.models import Sum
from .models import Sale, SaleItem, Customer, Product, SalesReturn,SalesTarget, Notification
from users.models import CustomUser
import json
from django.utils import timezone
from datetime import timedelta
from .models import SalesTarget, TopSellingProduct, TopCustomer
from .forms import CustomerForm
from users.models import SiteSettings
from .forms import NewSaleForm, DiscountForm, ReceiptForm
from .models import Sale, Discount, Receipt
from .forms import ReturnExchangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from .models import Menu
from django.urls import reverse




def get_sales_dashboard_context(request):
    settings = SiteSettings.objects.first()
    today = timezone.now().date()
    this_month = timezone.now().month

    today_sales_qs = Sale.objects.filter(date__date=today, cashier=request.user)
    total_sales_today = today_sales_qs.aggregate(Sum('total'))['total__sum'] or 0
    transaction_count = today_sales_qs.count()

    best_selling_items = (
        SaleItem.objects.filter(sale__date__date=today, sale__cashier=request.user)
        .values('product__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )
    low_stock = Product.objects.filter(quantity__lte=5).order_by('quantity')[:5]
    recent_customers = Customer.objects.filter(sale__cashier=request.user).distinct().order_by('-id')[:5]
    sales_target = SalesTarget.objects.first()
    monthly_sales = Sale.objects.filter(
        date__month=this_month, cashier=request.user
    ).aggregate(Sum('total'))['total__sum'] or 0
    sales = Sale.objects.select_related('customer').filter(cashier=request.user).order_by('-date')[:20]
    best_selling_labels = [item['product__name'] for item in best_selling_items]
    best_selling_quantities = [item['total_quantity'] for item in best_selling_items]
    if not best_selling_labels:
        best_selling_labels = ['No Sales Yet']
        best_selling_quantities = [1]
    # Add forms for modals
    new_sale_form = NewSaleForm()
    return_form = ReturnExchangeForm()
    discount_form = DiscountForm()
    receipt_form = ReceiptForm()
    customer_form = CustomerForm()
    context = {
        'total_sales': Sale.objects.aggregate(total=Sum('total'))['total'] or 0,
        'total_sales_today': total_sales_today,
        'transaction_count': transaction_count,
        'sales': sales,
        'best_selling_items': best_selling_items,
        'low_stock': low_stock,
        'recent_customers': recent_customers,
        'sales_target': sales_target,
        'monthly_sales': monthly_sales,
        'best_selling_labels': best_selling_labels,
        'best_selling_quantities': best_selling_quantities,
        'site_settings': settings,
        'form_new_sale': new_sale_form,
        'form_return': return_form,
        'form_discount': discount_form,
        'form_receipt': receipt_form,
        'customer_form': customer_form,
    }
    return context


# Update sales_dashboard to use the helper
@login_required
def sales_dashboard(request):
    context = get_sales_dashboard_context(request)
    return render(request, 'pos/sales_dashboard.html', context)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def create_sale(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data."}, status=400)

        customer_id = data.get("customer_id")
        items = data.get("items")
        amount_paid = data.get("amount")

        if not items or not isinstance(items, list):
            return JsonResponse({"success": False, "error": "No products added."}, status=400)

        customer = Customer.objects.filter(id=customer_id).first() or Customer.objects.first()
        sale = Sale.objects.create(customer=customer, total=0, cashier=request.user)
        total = 0
        out_of_stock = []
        item_summary = []

        for item in items:
            try:
                product = Product.objects.get(id=item["product_id"])
                quantity = int(item["quantity"])
                if product.quantity < quantity:
                    out_of_stock.append(product.name)
                    continue
                subtotal = product.price * quantity

                # Save SaleItem
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                    subtotal=subtotal
                )

                # Update stock
                product.quantity -= quantity
                product.save()

                # Track for receipt
                total += subtotal
                item_summary.append({
                    "product": product.name,
                    "quantity": quantity,
                    "unit_price": float(product.price),
                    "subtotal": float(subtotal)
                })

            except Product.DoesNotExist:
                continue

        if out_of_stock:
            sale.delete()
            return JsonResponse({"success": False, "error": f"Not enough stock for: {', '.join(out_of_stock)}."}, status=400)

        sale.total = total
        sale.save()
        Receipt.objects.create(sale=sale)

        return JsonResponse({
            "success": True,
            "sale_id": sale.id,
            "customer": customer.name,
            "items": item_summary,
            "total": float(total)
        })

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)


@login_required
def sale_detail(request, sale_id):
    sale = Sale.objects.select_related('customer').get(id=sale_id)
    items = SaleItem.objects.filter(sale=sale)
    return render(request, 'pos/sale_detail.html', {'sale': sale, 'items': items})


@login_required
def supervisor_dashboard(request):
    # Restrict access to supervisors only
    if not hasattr(request.user, 'role') or request.user.role != 'supervisor':
        return redirect('users:login')

    # Get all salespersons and calculate performance stats
    salespersons = CustomUser.objects.filter(role='salesperson')
    performance = []

    for sp in salespersons:
        sales = Sale.objects.filter(cashier=sp)
        total_sales = sales.aggregate(total=Sum('total'))['total'] or 0
        num_sales = sales.count()
        total_quantity = SaleItem.objects.filter(sale__cashier=sp).aggregate(qty=Sum('quantity'))['qty'] or 0

        performance.append({
            'salesperson': sp,
            'total_sales': total_sales,
            'num_sales': num_sales,
            'total_quantity': total_quantity,
        })

    performance.sort(key=lambda x: x['total_sales'], reverse=True)

    # Summary statistics
    total_sales = Sale.objects.aggregate(total=Sum('total'))['total'] or 0
    total_returns = SalesReturn.objects.aggregate(total=Sum('amount'))['total'] or 0
    products = Product.objects.all()
    recent_returns = SalesReturn.objects.select_related('sale', 'sale__customer').order_by('-sale__timestamp')[:10]

    # Site Settings (for logo, etc.)
    site_settings = SiteSettings.objects.first()

    # Menus with submenus, including dynamically injected submenus under "Transactions"
    menus_qs = Menu.objects.prefetch_related('submenus').order_by('order')
    menus = []

    for menu in menus_qs:
        submenu_items = list(menu.submenus.all())  # existing submenus from DB

        # Inject default submenu items under "Transactions"
        if menu.name.lower() == 'transactions':
            existing_names = [sm.name.lower() for sm in submenu_items]

            default_submenus = [
                {'name': 'Sales', 'url': reverse('sales:sales_list'), 'icon': 'icons/sales.png'},
                {'name': 'Purchases', 'url': reverse('purchases:purchases_list'), 'icon': 'icons/purchases.png'},
                {'name': 'Sales Return', 'url': reverse('sales:sales_returns'), 'icon': 'icons/sales_return.png'},
                {'name': 'Purchases Return', 'url': reverse('purchases:purchases_returns'), 'icon': 'icons/purchases_return.png'},
            ]

            for item in default_submenus:
                if item['name'].lower() not in existing_names:
                    # Dynamically create a pseudo-submenu object to match template expectations
                    submenu_items.append(type('SubmenuObject', (), {
                        'name': item['name'],
                        'url': item['url'],
                        'icon': item['icon']
                    })())

        # Append menu and submenus (as objects) to context
        menus.append({
            'id': menu.id,
            'name': menu.name,
            'submenus': submenu_items
        })

    # Render dashboard with all necessary context
    return render(request, 'pos/supervisor_dashboard.html', {
        'performance': performance,
        'total_sales': total_sales,
        'total_returns': total_returns,
        'products': products,
        'recent_returns': recent_returns,
        'site_settings': site_settings,
        'menus': menus,
    })

@login_required
def new_sale(request):
    if request.method == 'POST':
        form = NewSaleForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            if product.quantity < quantity:
                messages.error(request, "Not enough stock for this product.")
                return redirect('pos:new_sale')
            # Deduct stock
            product.quantity -= quantity
            product.save()
            # Create sale and sale item
            sale = Sale.objects.create(customer=None, total=product.price * quantity, cashier=request.user)
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=product.price,
                subtotal=product.price * quantity
            )
            # Generate receipt
            receipt = Receipt.objects.create(sale=sale)
            return redirect('pos:sale_receipt', sale_id=sale.id)
    else:
        form = NewSaleForm()
    return render(request, 'pos/new_sale.html', {'form': form})


@login_required
def return_item(request):
    """
    Handles item returns/exchanges. On GET, displays form. On POST, processes the form.
    """
    if request.method == 'POST':
        form = ReturnExchangeForm(request.POST)  # Add request.FILES if needed
        if form.is_valid():
            # Implement return logic here
            # e.g., update inventory, mark order as returned, issue refund
            return redirect('pos:sales_dashboard')
    else:
        form = ReturnExchangeForm()

    context = {'form': form}
    return render(request, 'pos/return_items.html', context)

def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            # After successful registration, reload dashboard with success message
            messages.success(request, 'Customer registered successfully!')
            return redirect('pos:sales_dashboard')
        # If form is invalid, re-render dashboard with errors in modal
        dashboard_context = get_sales_dashboard_context(request)
        dashboard_context['customer_form'] = form
        return render(request, 'pos/sales_dashboard.html', dashboard_context)
    else:
        return redirect('pos:sales_dashboard')

def issue_receipt(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        if form.is_valid():
            sale = form.cleaned_data['sale']
            Receipt.objects.create(sale=sale)
            return render(request, 'pos/receipt_issued.html', {'sale': sale})
    else:
        form = ReceiptForm()
    return render(request, 'pos/issue_receipt.html', {'form': form})

# views.py

@login_required
def return_exchange(request):
    if request.method == 'POST':
        form = ReturnExchangeForm(request.POST)
        if form.is_valid():
            sale = form.cleaned_data['sale']
            return_type = form.cleaned_data['return_type']
            new_product = form.cleaned_data.get('new_product')

            sale.is_returned = True

            if return_type == 'exchange':
                sale.is_exchange = True
                sale.exchange_for = new_product
                # optional: charge/refund difference in price

            sale.save()
            return redirect('pos:sales_dashboard')
    else:
        form = ReturnExchangeForm()

    return render(request, 'pos/return_exchange.html', {'form': form})


# ✅ Second one (decorated, newer)
@permission_required('pos.can_apply_discount', raise_exception=True)
def apply_discount(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            discount = form.save()

            # Apply discounted price to the product
            product = discount.product
            discount_amount = product.price * (discount.percentage / 100)
            new_price = product.price - discount_amount
            product.price = new_price
            product.save()

            messages.success(request, f"{discount.percentage}% discount applied to {product.name}. New price: {new_price:.2f}")
            return redirect('pos:sales_dashboard')
    else:
        form = DiscountForm()

    return render(request, 'pos/apply_discount.html', {'form': form})

def search_product(request):
    query = request.GET.get("query", "")
    products = Product.objects.filter(name__icontains=query) | Product.objects.filter(barcode__icontains=query)
    data = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "barcode": p.barcode,
            "stock": p.stock
        }
        for p in products
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def create_sale(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"success": False, "error": "Invalid JSON data."}, status=400)

        customer_id = data.get("customer_id")
        items = data.get("items")
        amount_paid = data.get("amount")

        if not items or not isinstance(items, list):
            return JsonResponse({"success": False, "error": "No products added."}, status=400)

        customer = Customer.objects.filter(id=customer_id).first() or Customer.objects.first()
        sale = Sale.objects.create(customer=customer, total=0)
        total = 0
        out_of_stock = []

        for item in items:
            try:
                product = Product.objects.get(id=item["product_id"])
                quantity = int(item["quantity"])
                if product.quantity < quantity:
                    out_of_stock.append(product.name)
                    continue
                subtotal = product.price * quantity
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                    subtotal=subtotal
                )
                product.quantity -= quantity
                product.save()
                total += subtotal
            except Product.DoesNotExist:
                continue

        if out_of_stock:
            sale.delete()
            return JsonResponse({"success": False, "error": f"Not enough stock for: {', '.join(out_of_stock)}."}, status=400)

        sale.total = total
        sale.save()
        receipt = Receipt.objects.create(sale=sale)
        return JsonResponse({"success": True, "sale_id": sale.id})

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)
def sale_receipt(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)
    return render(request, 'pos/receipt.html', {'sale': sale})

@require_GET
def product_search(request):
    query = request.GET.get("query", "").strip()
    try:
        product = Product.objects.get(barcode=query)
    except Product.DoesNotExist:
        try:
            product = Product.objects.filter(name__icontains=query).first()
        except Product.DoesNotExist:
            product = None

    if product:
        return JsonResponse({
            "product": {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "stock": product.stock
            }
        })
    else:
        return JsonResponse({"product": None})

def new_pos_sale(request):
    return render(request, 'pos/new_pos_sale.html')


from django.http import JsonResponse

def ajax_get_product(request):
    barcode = request.GET.get('barcode')
    if not barcode:
        return JsonResponse({'success': False, 'error': 'No barcode provided'})
    try:
        product = Product.objects.get(code=barcode)
        return JsonResponse({'success': True, 'name': product.name})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})