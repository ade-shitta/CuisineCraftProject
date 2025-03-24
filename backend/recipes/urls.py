from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('<int:recipe_id>/favorite/', views.toggle_favorite_recipe, name='toggle_favorite_recipe'),
    path('favorites/', views.favorite_recipes, name='favorite_recipes'),
    path('search/', views.search_recipes, name='search_recipes'),
]