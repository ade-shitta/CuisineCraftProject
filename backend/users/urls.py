from django.urls import path
from . import views
from . import api
from .api import AuthCheckView 

urlpatterns = [
    # Regular Django views
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # API endpoints
    path('api/csrf/', api.CSRFTokenView.as_view(), name='api-csrf'),
    path('api/register/', api.UserRegistrationView.as_view(), name='api-register'),
    path('api/login/', api.UserLoginView.as_view(), name='api-login'),
    path('api/logout/', api.UserLogoutView.as_view(), name='api-logout'),
    path('api/profile/', api.UserProfileView.as_view(), name='api-profile'),
    path('api/authenticated/', AuthCheckView.as_view(), name='auth_check'),
]
