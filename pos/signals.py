from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SaleItem
from .models import Sale, TopSellingProduct
from django.db.models import Sum
from .utils import update_weekly_data
from .models import CustomUser, Customer

@receiver(post_save, sender=SaleItem)
def update_stock(sender, instance, created, **kwargs):
    if created and instance.product:
        instance.product.quantity_in_stock -= instance.quantity
        instance.product.save()

@receiver(post_save, sender=Sale)
def update_top_selling_products(sender, instance, **kwargs):
    top_sales = (
        Sale.objects
        .values('product')
        .annotate(total_sold=Sum('quantity_sold'))
        .order_by('-total_sold')[:6]
    )

    TopSellingProduct.objects.all().delete()  # Clear old data
    for entry in top_sales:
        TopSellingProduct.objects.create(
            product_id=entry['product'],
            total_sold=entry['total_sold']
        )

@receiver(post_save, sender=CustomUser)
def create_customer_for_user(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'customer'):
        Customer.objects.create(user=instance, name=instance.username, email=instance.email)