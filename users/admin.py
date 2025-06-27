from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UISettings
from .models import LandingPageContent
from modeltranslation.admin import TranslationAdmin
from .models import SiteSettings

# Register your models here.
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'is_active', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'is_approved')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'is_approved')}),
    )

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name']

@admin.register(LandingPageContent)
class LandingPageContentAdmin(TranslationAdmin):
    pass

admin.site.register(UISettings)


