from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm
from recipes.models import SavedRecipe

# Create your views here.
# @login_required
def home(request: HttpRequest) -> HttpResponse:
    # if not request.user.is_authenticated:
    #     return redirect('login')
    return render(request, 'spa/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        print(f"Form submitted with data: {request.POST}")
        if form.is_valid():
            print("Form is valid, creating user")
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            print(f"Form validation errors: {form.errors}")
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'auth/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    # Count saved recipes
    saved_recipes_count = SavedRecipe.objects.filter(user=request.user).count()
    
    return render(request, 'users/profile.html', {
        'saved_recipes_count': saved_recipes_count
    })

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        
        # Handle profile image upload
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
            
        user.save()
        return redirect('profile')
        
    return redirect('profile')