from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'), 
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_user, name='logout'),

    # Dashboards
    path('admin-dashboard/', views.dashboard_view, name='admin_dashboard'),
    path('supervisor-dashboard/', views.dashboard_view, name='supervisor_dashboard'),
    path('sales-rep-dashboard/', views.dashboard_view, name='sales_rep_dashboard'),

    # Products
    path('create-product/', views.create_product, name='create_product'),
    path('product_list/', views.product_list_view, name='product_list'),
    path('products-cards/', views.product_cards, name='product_cards'),
    path('success/', views.product_success, name='product_success'),
    path('export-products-excel/', views.export_products_excel, name='export_products_excel'),
    path('export-products-pdf/', views.export_products_pdf, name='export_products_pdf'),
    path('products/print-barcode/', views.print_barcode_view, name='print_barcode'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:order_id>/summary/', views.order_summary, name='order_summary'),
]
