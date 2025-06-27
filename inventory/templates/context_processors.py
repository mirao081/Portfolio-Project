
from .models import Country

def country_list(request):
    return {
        'countries': Country.objects.all()
    }
