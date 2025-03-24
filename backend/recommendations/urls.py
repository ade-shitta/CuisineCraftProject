from django.urls import path
from . import views

urlpatterns = [
    path('preferences/', views.preferences, name='dietary_preferences'),
    path('recommended/', views.recommended_recipes, name='recommended_recipes'),
]