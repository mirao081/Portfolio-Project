# Generated by Django 5.2 on 2025-06-26 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0010_alter_discount_product_alter_stockalert_product_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='product',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='quantity',
        ),
    ]
