from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UISettings
from .models import LandingPageContent
from modeltranslation.admin import TranslationAdmin
from .models import SiteSettings

# Register your models here.
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'is_approved', 'profile_picture'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'is_approved', 'profile_picture'),
        }),
    )

    list_display = ('username', 'email', 'role', 'is_approved')
    list_filter = ('role', 'is_approved')

admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name']

@admin.register(LandingPageContent)
class LandingPageContentAdmin(TranslationAdmin):
    pass

admin.site.register(UISettings)


