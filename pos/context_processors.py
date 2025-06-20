from .models import UISettings, Country

def ui_settings_context(request):  # ✅ Rename to match settings.py
    return {
        'ui_settings': UISettings.objects.first()
    }

def country_list(request):
    countries = Country.objects.all()
    return {'countries': countries}
