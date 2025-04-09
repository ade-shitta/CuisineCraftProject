from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    UserChangeForm,
    PasswordChangeForm,
)
from .models import User

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter a username'
        })
    )
    first_name = forms.CharField(required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@example.com'
        })
    )
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'placeholder': 'DD/MM/YYYY',
            'type': 'date'  # Use HTML5 date input
        }),
        input_formats=['%d/%m/%Y', '%Y-%m-%d']  # Support multiple formats
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
        fields = ('username','first_name', 'last_name', 'email', 'date_of_birth', 'password1', 'password2')

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username'
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
        fields = ("username", "password")

class UserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

class UserPasswordUpdateForm(PasswordChangeForm):
    # This will leverage Django's built-in PasswordChangeForm i think? (not figured this out yet)
    # No Meta class is necessary since it's not a ModelForm. (thank stack overflow for this explanation)
    pass