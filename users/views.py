from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from users.models import UISettings
from .models import LandingPageContent
from django.utils.translation import activate
from django.utils import translation
from .forms import ProfileUpdateForm



# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Prevent login until approved
            user.save()
            # Optionally notify manager for approval
            return render(request, 'users/registration_pending.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_approved:
                login(request, user)
                # Redirect based on role
                if user.role == 'salesperson':
                    return redirect('pos:sales_dashboard')  # URL name for sales dashboard
                elif user.role == 'manager':
                    return redirect('pos:manager_dashboard')  # URL name for manager dashboard
                elif user.role == 'supervisor':
                    return redirect('pos:supervisor_dashboard')  # URL name for supervisor dashboard
                else:
                    return redirect('users:index')  # fallback
            else:
                messages.error(request, 'Your account is pending manager approval.')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'users/login.html')

def index(request):
    lang = request.GET.get('lang')
    if lang:
        activate(lang)
        request.session['django_language'] = lang
    ui_settings = UISettings.objects.first()
    content = LandingPageContent.objects.first()
    return render(request, 'users/index.html', {
        'ui_settings': ui_settings,
        'content': content,
    })

def approve_user(request, user_id):
    # Placeholder for manager approval logic
    return render(request, 'users/approve_user.html', {'user_id': user_id})

def custom_logout(request):
    logout(request)
    return redirect('users:login')

@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user, user=user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')  # Redirect to some profile view or dashboard
    else:
        form = ProfileUpdateForm(instance=user, user=user)
    return render(request, 'users/update_profile.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})
