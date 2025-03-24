import numpy as np
from django.db.models import Count, Q
from recommendations.text_utils import find_similar_recipes
from recipes.models import Recipe, SavedRecipe, RecipeIngredient
from recommendations.models import RecipeInteraction, DietaryPreference

def get_user_dietary_preferences(user):
    """Get user's dietary preferences"""
    if not user.is_authenticated:
        return []
    
    preferences = DietaryPreference.objects.filter(user=user).values_list('restriction_type', flat=True)
    return list(preferences)

def filter_by_dietary_preferences(recipes_queryset, preferences):
    """Filter recipes by dietary preferences"""
    if not preferences:
        return recipes_queryset
    
    # SQLite doesn't support JSON contains lookup, so filter in Python
    all_recipes = list(recipes_queryset)
    matching_recipe_ids = []
    
    # Check each recipe against all preferences
    for recipe in all_recipes:
        if all(pref in recipe.dietary_tags for pref in preferences):
            matching_recipe_ids.append(recipe.recipe_id)
    
    # Return filtered queryset based on collected IDs
    if matching_recipe_ids:
        return recipes_queryset.filter(recipe_id__in=matching_recipe_ids)
    else:
        return Recipe.objects.none()

def get_user_favorite_ingredients(user, top_n=5):
    """Get user's most frequently favorited ingredients"""
    if not user.is_authenticated:
        return []
    
    # Get ingredients from user's saved recipes
    favorite_recipe_ids = SavedRecipe.objects.filter(user=user).values_list('recipe_id', flat=True)
    
    if not favorite_recipe_ids:
        return []
    
    # Get most common ingredients in favorited recipes
    favorite_ingredients = (
        RecipeIngredient.objects.filter(recipe_id__in=favorite_recipe_ids)
        .values('ingredient_id')
        .annotate(count=Count('ingredient_id'))
        .order_by('-count')[:top_n]
        .values_list('ingredient_id', flat=True)
    )
    
    return list(favorite_ingredients)

def get_content_based_recommendations(user, max_results=10):
    """Get content-based recommendations using text similarity and user preferences"""
    if not user.is_authenticated:
        return Recipe.objects.none()
    
    # Get user's favorite recipes
    favorite_recipe_ids = list(SavedRecipe.objects.filter(user=user).values_list('recipe_id', flat=True))
    
    if not favorite_recipe_ids:
        # If no favorites, return popular recipes
        popular_recipes = Recipe.objects.annotate(
            save_count=Count('saved_instances')
        ).order_by('-save_count')[:max_results]
        
        return popular_recipes
    
    # Get content-based recommendations from each favorite recipe
    recommended_recipe_ids = set()
    
    for recipe_id in favorite_recipe_ids:
        similar_recipes = find_similar_recipes(recipe_id, top_n=3)
        recommended_recipe_ids.update(similar_recipes)
    
    # Remove recipes the user has already favorited
    recommended_recipe_ids = recommended_recipe_ids - set(favorite_recipe_ids)
    
    # Get the actual recipe objects
    recommended_recipes = Recipe.objects.filter(recipe_id__in=recommended_recipe_ids)
    
    # Get user's dietary preferences
    preferences = get_user_dietary_preferences(user)
    
    # Filter by dietary preferences
    if preferences:
        recommended_recipes = filter_by_dietary_preferences(recommended_recipes, preferences)
    
    # Limit to max_results
    return recommended_recipes[:max_results]

def get_recent_interactions(user, interaction_type='view', limit=5):
    """Get user's recent recipe interactions of a specific type"""
    if not user.is_authenticated:
        return []
    
    recent_interactions = RecipeInteraction.objects.filter(
        user=user, 
        interaction_type=interaction_type
    ).order_by('-timestamp')[:limit]
    
    return [interaction.recipe_id for interaction in recent_interactions]

def get_personalized_recommendations(user, max_results=12):
    """Get personalized recipe recommendations for a user"""
    # Get content-based recommendations
    content_based = get_content_based_recommendations(user, max_results=max_results)
    
    # If content_based is already a list, check its length directly
    content_based_count = len(content_based) if isinstance(content_based, list) else content_based.count()
    
    # Get user's dietary preferences
    preferences = get_user_dietary_preferences(user)
    
    # If we have fewer than max_results, add popular recipes
    if content_based_count < max_results:
        # Get popular recipes
        popular_recipes = Recipe.objects.annotate(
            save_count=Count('saved_instances')
        ).order_by('-save_count')
        
        # Filter by dietary preferences
        if preferences:
            popular_recipes = filter_by_dietary_preferences(popular_recipes, preferences)
        
        # Ensure content_based is a list for the rest of the operations
        if not isinstance(content_based, list):
            content_based = list(content_based)
            
        # Get IDs of already recommended recipes
        existing_ids = [recipe.recipe_id for recipe in content_based]
        
        # Exclude already recommended recipes
        popular_filtered = [recipe for recipe in popular_recipes 
                           if recipe.recipe_id not in existing_ids]
        
        # Add popular recipes to fill up to max_results
        needed = max_results - len(content_based)
        content_based.extend(popular_filtered[:needed])
    
    return content_based