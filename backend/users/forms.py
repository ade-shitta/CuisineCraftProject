from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    UserChangeForm,
    PasswordChangeForm,
)
from .models import User

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'John Doe'
        })
    )
    last_name = forms.CharField(required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'John Doe'
        })
    )
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@example.com'
        })
    )
    date_of_birth = forms.DateField(required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'placeholder': 'DD/MM/YYY'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'date_of_birth', 'password1', 'password2')

class UserLoginForm(AuthenticationForm):
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        })
    )
    
    class Meta:
        model = User
        fields = ("email", "password")

class UserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

class UserPasswordUpdateForm(PasswordChangeForm):
    # This will leverage Django's built-in PasswordChangeForm i think? (not figured this out yet)
    # No Meta class is necessary since it's not a ModelForm. (thank stack overflow for this explanation)
    pass