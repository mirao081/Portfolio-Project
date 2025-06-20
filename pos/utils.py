from datetime import date
from .models import WeeklySalesData

def update_weekly_data(entry_type, amount):
    today = date.today()
    weekly_entry, created = WeeklySalesData.objects.get_or_create(day=today)

    if entry_type == 'sale':
        weekly_entry.sales += amount
    elif entry_type == 'purchase':
        weekly_entry.purchases += amount

    weekly_entry.save()