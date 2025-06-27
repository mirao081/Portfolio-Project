from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'pos'

app_name = 'pos'
urlpatterns = [
    path('sales/', views.sales_dashboard, name='sales_dashboard'),
    path('sales/create/', views.create_sale, name='create_sale'),
    path('sales/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('supervisor-dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='pos/login.html'), name='login'),
    path('return/', views.return_item, name='return_item'),
    path('receipt/', views.issue_receipt, name='issue_receipt'),
    path('customer/add/', views.add_customer, name='add_customer'),

    path('apply-discount/', views.apply_discount, name='apply_discount'),
    path('issue-receipt/', views.issue_receipt, name='issue_receipt'),
    path('receipt/<int:sale_id>/', views.sale_receipt, name='sale_receipt'),
    path("pos/", views.new_pos_sale, name="pos_interface"),
    path('ajax/get-product/', views.ajax_get_product, name='ajax_get_product'),
]
