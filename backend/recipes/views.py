from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Recipe, SavedRecipe
from recommendations.models import DietaryPreference

def recipe_list(request):
    """Display a list of recipes, filtered by user's dietary preferences if available."""
    # Start with all recipes
    recipes = Recipe.objects.all()
    
    # If user is logged in, check for dietary preferences
    has_preferences = False
    filtered_by_preferences = False
    user_preferences = []
    
    if request.user.is_authenticated:
        user_preferences = list(DietaryPreference.objects.filter(user=request.user).values_list('restriction_type', flat=True))
        has_preferences = bool(user_preferences)
        
        if has_preferences:
            # SQLite doesn't support JSON contains lookup, so we'll filter in Python
            all_recipes = list(recipes)
            filtered_recipes = []
            
            for recipe in all_recipes:
                # Check if recipe matches all user preferences
                if all(pref in recipe.dietary_tags for pref in user_preferences):
                    filtered_recipes.append(recipe.recipe_id)
            
            # Filter the queryset by IDs we collected
            if filtered_recipes:
                recipes = recipes.filter(recipe_id__in=filtered_recipes)
                filtered_by_preferences = True
            else:
                # No recipes match the preferences
                recipes = Recipe.objects.none()
                filtered_by_preferences = True
    
    # Order recipes by title
    recipes = recipes.order_by('title')
    
    # Set up pagination - 12 recipes per page
    paginator = Paginator(recipes, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'recipes/recipe_list.html', {
        'recipes': page_obj,
        'page_obj': page_obj,
        'has_preferences': has_preferences,
        'filtered_by_preferences': filtered_by_preferences
    })

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

@login_required
def save_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    # Check if the recipe is already saved to prevent duplicates
    SavedRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    return redirect('recipe_detail', recipe_id=recipe_id)