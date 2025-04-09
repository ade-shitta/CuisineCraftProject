from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Recipe, SavedRecipe, RecipeIngredient
from recommendations.models import DietaryPreference, RecipeInteraction
from recommendations.text_utils import search_by_ingredients
from rest_framework import serializers

def recipe_list(request):
    """Display a list of recipes, filtered by user's dietary preferences if available."""
    # Start with all recipes
    recipes = Recipe.objects.all()
    
    # If user is logged in, check for dietary preferences
    has_preferences = False
    filtered_by_preferences = False
    user_preferences = []
    favorite_recipe_ids = set()
    
    if request.user.is_authenticated:
        user_preferences = list(DietaryPreference.objects.filter(user=request.user).values_list('restriction_type', flat=True))
        has_preferences = bool(user_preferences)
        
        # Get user's favorite recipe IDs
        favorite_recipe_ids = set(SavedRecipe.objects.filter(user=request.user).values_list('recipe__recipe_id', flat=True))
        
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
        'filtered_by_preferences': filtered_by_preferences,
        'favorite_recipe_ids': favorite_recipe_ids  # Pass favorite recipe IDs to template
    })

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    # Record view interaction
    if request.user.is_authenticated:
        RecipeInteraction.objects.create(
            user=request.user,
            recipe=recipe,
            interaction_type='view'
        )
    
    # Check if the recipe is favorited by current user
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = SavedRecipe.objects.filter(user=request.user, recipe=recipe).exists()
    
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'is_favorite': is_favorite
    })

@login_required
def save_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    # Check if the recipe is already saved to prevent duplicates
    SavedRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    return redirect('recipe_detail', recipe_id=recipe_id)

@login_required
def toggle_favorite_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    # Check if recipe is already saved
    saved_recipe = SavedRecipe.objects.filter(user=request.user, recipe=recipe).first()
    
    if saved_recipe:
        # If already favorited, remove it
        saved_recipe.delete()
        interaction_type = 'unfavorite'
    else:
        # If not favorited, add it
        SavedRecipe.objects.create(user=request.user, recipe=recipe)
        interaction_type = 'favorite'
        
        # Record favorite interaction
        RecipeInteraction.objects.create(
            user=request.user,
            recipe=recipe,
            interaction_type='favorite'
        )
    
    # Redirect back to the page they were on or to the recipe detail page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('recipe_detail', recipe_id=recipe_id)

@login_required
def favorite_recipes(request):
    saved_recipes = SavedRecipe.objects.filter(user=request.user).select_related('recipe')
    
    # Extract recipe objects for display
    recipes = [saved.recipe for saved in saved_recipes]
    
    return render(request, 'recipes/favorite_recipes.html', {
        'recipes': recipes,
        'is_favorites_page': True
    })

def search_recipes(request):
    """Search for recipes by ingredient, respecting dietary preferences"""
    query = request.GET.get('ingredients', '')
    
    if query:
        # Pass the current user to apply dietary preferences
        recipes = search_by_ingredients(query, user=request.user)
    else:
        # Don't apply slice yet - get all recipes first
        recipes = Recipe.objects.all()
        
        # Apply dietary filtering for default results if user is logged in
        if request.user.is_authenticated:
            from recommendations.models import DietaryPreference
            preferences = list(DietaryPreference.objects.filter(
                user=request.user
            ).values_list('restriction_type', flat=True))
            
            if preferences:
                # Use a different approach to filter by preferences
                # Create a list to store recipes that match all preferences
                matching_recipe_ids = []
                
                for recipe in recipes:
                    if all(pref in recipe.dietary_tags for pref in preferences):
                        matching_recipe_ids.append(recipe.recipe_id)
                
                # Then filter the original queryset
                recipes = Recipe.objects.filter(recipe_id__in=matching_recipe_ids)
        
        # Apply limit AFTER all filtering
        recipes = recipes[:12]
    
    # Get user's favorite recipe IDs for UI if logged in
    favorite_recipe_ids = set()
    if request.user.is_authenticated:
        favorite_recipe_ids = set(SavedRecipe.objects.filter(
            user=request.user
        ).values_list('recipe__recipe_id', flat=True))
    
    # Check if we're filtering by preferences
    has_preferences = False
    filtered_by_preferences = False
    if request.user.is_authenticated:
        from recommendations.models import DietaryPreference
        preferences = DietaryPreference.objects.filter(user=request.user)
        has_preferences = preferences.exists()
        filtered_by_preferences = has_preferences
    
    return render(request, 'recipes/search_results.html', {
        'recipes': recipes,
        'query': query,
        'favorite_recipe_ids': favorite_recipe_ids,
        'has_preferences': has_preferences,
        'filtered_by_preferences': filtered_by_preferences
    })

class IngredientSerializer(serializers.Serializer):
    name = serializers.CharField()
    amount = serializers.CharField()

class RecipeDetailSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = ['recipe_id', 'title', 'instructions', 'dietary_tags', 'image_url', 'ingredients']
    
    def get_ingredients(self, obj):
        ingredients = []
        for ri in obj.recipe_ingredients.all():
            ingredients.append({
                'name': ri.ingredient.name,
                'amount': ri.measurement
            })
        return ingredients

@login_required
def mark_recipe_cooked(request, recipe_id):
    """Mark a recipe as cooked by the user"""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    # Record cook interaction
    RecipeInteraction.objects.create(
        user=request.user,
        recipe=recipe,
        interaction_type='cook'
    )
    
    # Redirect back to referrer
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('recipe_detail', recipe_id=recipe_id)