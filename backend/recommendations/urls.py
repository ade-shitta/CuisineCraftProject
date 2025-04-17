from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Regular Django views
    path('preferences/', views.preferences, name='dietary_preferences'),
    path('recommended/', views.recommended_recipes, name='recommended_recipes'),
    
    # API endpoints
    path('api/preferences/', api.DietaryPreferenceView.as_view(), name='api-dietary-preferences'),
    path('api/recommended/', api.RecommendedRecipesView.as_view(), name='api-recommended-recipes'),
    path('api/almost-matching/', api.AlmostMatchingRecipesView.as_view(), name='api-almost-matching-recipes'),
]