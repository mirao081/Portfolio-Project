from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('profile/edit/', views.update_profile, name='profile_edit'),
    path('profile/', views.profile_view, name='profile'),
    
    # ... other URLs ...
]