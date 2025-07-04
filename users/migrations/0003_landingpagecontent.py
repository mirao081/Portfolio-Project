# Generated by Django 5.2 on 2025-06-23 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_uisettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='LandingPageContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hero_title', models.CharField(max_length=255)),
                ('hero_subtitle', models.TextField()),
                ('about_us', models.TextField()),
                ('what_we_do', models.TextField()),
                ('contact_email', models.EmailField(max_length=254)),
                ('contact_phone', models.CharField(max_length=20)),
                ('contact_address', models.TextField()),
            ],
        ),
    ]
