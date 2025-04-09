from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Regular Django views
    path('', views.recipe_list, name='recipe_list'),
    path('<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('<int:recipe_id>/favorite/', views.toggle_favorite_recipe, name='toggle_favorite_recipe'),
    path('favorites/', views.favorite_recipes, name='favorite_recipes'),
    path('search/', views.search_recipes, name='search_recipes'),
    path('recipe/<int:recipe_id>/cook/', views.mark_recipe_cooked, name='mark_recipe_cooked'),
    
    # API endpoints
    path('api/', api.RecipeListView.as_view(), name='api-recipes'),
    path('api/<int:recipe_id>/', api.RecipeDetailView.as_view(), name='api-recipe-detail'),
    path('api/<int:recipe_id>/favorite/', api.ToggleFavoriteView.as_view(), name='api-toggle-favorite'),
    path('api/favorites/', api.FavoriteRecipesView.as_view(), name='api-favorite-recipes'),
    path('api/<int:recipe_id>/toggle-favorite/', api.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('api/<int:recipe_id>/cook/', api.MarkRecipeCookedView.as_view(), name='api-mark-recipe-cooked'),
]