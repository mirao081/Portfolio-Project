from django import forms
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password']
        help_texts = {
            'username': '',  # Remove the default help text
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'profile_picture', 'role']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # The currently logged-in user
        super().__init__(*args, **kwargs)

        if user and not (user.is_superuser or user.role == 'manager'):
            # Make 'role' read-only or hide it
            del self.fields['role']