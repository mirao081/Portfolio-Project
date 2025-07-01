from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('supervisor', 'Supervisor'),
        ('salesperson', 'Salesperson'),
    ]
    role = models.CharField(max_length=20, choices=[('supervisor', 'Supervisor'), ('salesperson', 'Salesperson')])
    is_approved = models.BooleanField(default=False)  # Only approved users can log in
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
class UISettings(models.Model):
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)

    def __str__(self):
        return "UI Settings"
    
class LandingPageContent(models.Model):
    hero_title = models.CharField(max_length=255)
    hero_subtitle = models.TextField()
    about_us = models.TextField()
    what_we_do = models.TextField()
    contact_us = models.TextField(null=True, blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    contact_address = models.TextField()

    def __str__(self):
        return "Landing Page Content"

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Sales Dashboard")
    logo = models.ImageField(upload_to='site_logos/', null=True, blank=True)

    def __str__(self):
        return self.site_name