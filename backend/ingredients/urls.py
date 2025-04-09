from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Regular Django views
    path('', views.ingredient_list, name='ingredient_list'),
    path('<int:ingredient_id>/', views.ingredient_detail, name='ingredient_detail'),
    path('<int:ingredient_id>/track/', views.track_ingredient, name='track_ingredient'),
    path('<int:ingredient_id>/untrack/', views.untrack_ingredient, name='untrack_ingredient'),
    
    # API endpoints
    path('api/', api.IngredientListView.as_view(), name='api-ingredients'),
    path('api/<int:ingredient_id>/', api.IngredientDetailView.as_view(), name='api-ingredient-detail'),
    path('api/user/', api.UserIngredientsView.as_view(), name='api-user-ingredients'),
    path('api/<int:ingredient_id>/track/', api.TrackIngredientView.as_view(), name='api-track-ingredient'),
    path('api/<int:ingredient_id>/untrack/', api.UntrackIngredientView.as_view(), name='api-untrack-ingredient'),
]