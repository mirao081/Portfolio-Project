from modeltranslation.translator import register, TranslationOptions
from .models import LandingPageContent

@register(LandingPageContent)
class LandingPageContentTranslationOptions(TranslationOptions):
    fields = (
        'hero_title',
        'hero_subtitle',
        'about_us',
        'what_we_do',
        'contact_us',
        'contact_email',
        'contact_phone',
        'contact_address',
    )