from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
] 