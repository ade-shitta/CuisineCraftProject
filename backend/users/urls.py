from django.urls import path
from . import views
from . import api
from .api import AuthCheckView 

urlpatterns = [
    # API endpoints only - remove the template views since we're using React
    path('csrf/', api.CSRFTokenView.as_view(), name='api-csrf'),
    path('register/', api.UserRegistrationView.as_view(), name='api-register'),
    path('login/', api.UserLoginView.as_view(), name='api-login'),
    path('logout/', api.UserLogoutView.as_view(), name='api-logout'),
    path('profile/', api.UserProfileView.as_view(), name='api-profile'),
    path('authenticated/', AuthCheckView.as_view(), name='auth_check'),
]
