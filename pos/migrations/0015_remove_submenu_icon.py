# Generated by Django 5.2 on 2025-07-01 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0014_alter_menu_options_menu_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submenu',
            name='icon',
        ),
    ]
