from django.contrib import admin
from .models import Recipe, SavedRecipe, RecipeIngredient

# Register your models here.
admin.site.register(Recipe)
admin.site.register(SavedRecipe)
admin.site.register(RecipeIngredient)
