import numpy as np
from django.db.models import Count, Q, F, ExpressionWrapper, fields, Sum
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from recommendations.text_utils import find_similar_recipes
from recipes.models import Recipe, SavedRecipe, RecipeIngredient
from recommendations.models import RecipeInteraction, DietaryPreference

# Cache TTLs (in seconds)
USER_RECOMMENDATIONS_TTL = 30 * 60  # 30 minutes
USER_FAVORITES_TTL = 60 * 60  # 1 hour
USER_PREFERENCES_TTL = 3 * 60 * 60  # 3 hours

def get_user_dietary_preferences(user):
    """Get user's dietary preferences with caching"""
    if not user.is_authenticated:
        return []
    
    # Try to get from cache
    cache_key = f'user_preferences_{user.id}'
    cached_preferences = cache.get(cache_key)
    
    if cached_preferences is not None:
        return cached_preferences
    
    # Not in cache, get from database
    preferences = DietaryPreference.objects.filter(user=user).values_list('restriction_type', flat=True)
    preferences_list = list(preferences)
    
    # Cache the result
    cache.set(cache_key, preferences_list, USER_PREFERENCES_TTL)
    
    return preferences_list

def filter_by_dietary_preferences(recipes_queryset, preferences):
    """Filter recipes by dietary preferences more efficiently"""
    if not preferences:
        return recipes_queryset
    
    # Instead of processing in batches, use more efficient filtering
    matching_recipes = []
    
    # Use select_related to reduce database queries
    for recipe in recipes_queryset.iterator():
        if all(pref in recipe.dietary_tags for pref in preferences):
            matching_recipes.append(recipe.recipe_id)
    
    # Return filtered queryset based on collected IDs
    if matching_recipes:
        return recipes_queryset.filter(recipe_id__in=matching_recipes)
    else:
        return Recipe.objects.none()

def get_user_favorite_ingredients(user, top_n=5):
    """Get user's most frequently favorited ingredients with caching"""
    if not user.is_authenticated:
        return []
    
    # Try to get from cache
    cache_key = f'user_favorite_ingredients_{user.id}'
    cached_ingredients = cache.get(cache_key)
    
    if cached_ingredients is not None:
        return cached_ingredients
    
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
    
    result = list(favorite_ingredients)
    
    # Cache the result
    cache.set(cache_key, result, USER_FAVORITES_TTL)
    
    return result

def get_content_based_recommendations(user, max_results=10):
    """Get content-based recommendations using text similarity and user preferences"""
    if not user.is_authenticated:
        return Recipe.objects.none()
    
    # Try to get from cache
    cache_key = f'content_recommendations_{user.id}_{max_results}'
    cached_recommendations = cache.get(cache_key)
    
    if cached_recommendations is not None:
        return Recipe.objects.filter(recipe_id__in=cached_recommendations)
    
    # Get user's favorite recipes
    favorite_recipe_ids = list(SavedRecipe.objects.filter(user=user).values_list('recipe_id', flat=True))
    
    if not favorite_recipe_ids:
        # If no favorites, return popular recipes
        popular_recipes = Recipe.objects.annotate(
            save_count=Count('saved_instances')
        ).order_by('-save_count')[:max_results]
        
        # Cache even the fallback results
        cache.set(
            cache_key, 
            [recipe.recipe_id for recipe in popular_recipes], 
            USER_RECOMMENDATIONS_TTL
        )
        
        return popular_recipes
    
    # Get content-based recommendations from each favorite recipe
    recommended_recipe_ids = set()
    
    # Limit the number of favorites we process to avoid too much processing
    for recipe_id in favorite_recipe_ids[:5]:  # Process at most 5 favorites
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
    
    # Store the recipe IDs in cache
    result_recipes = list(recommended_recipes[:max_results])
    result_ids = [recipe.recipe_id for recipe in result_recipes]
    cache.set(cache_key, result_ids, USER_RECOMMENDATIONS_TTL)
    
    # Limit to max_results
    return recommended_recipes[:max_results]

def get_recent_interactions(user, interaction_type='view', limit=5):
    """Get user's recent recipe interactions of a specific type"""
    if not user.is_authenticated:
        return []
    
    cache_key = f'user_interactions_{user.id}_{interaction_type}_{limit}'
    cached_interactions = cache.get(cache_key)
    
    if cached_interactions is not None:
        return cached_interactions
    
    recent_interactions = RecipeInteraction.objects.filter(
        user=user, 
        interaction_type=interaction_type
    ).order_by('-timestamp')[:limit]
    
    result = [interaction.recipe_id for interaction in recent_interactions]
    
    # Cache for a shorter period since interactions change frequently
    cache.set(cache_key, result, 15 * 60)  # 15 minutes
    
    return result

def get_weighted_user_interactions(user, days_limit=30):
    """
    Get user interactions weighted by type and recency
    
    Weights:
    - favorite: 5.0
    - cook: 3.0
    - view: 1.0
    
    Also applies time decay - more recent interactions have higher weight
    """
    if not user.is_authenticated:
        return {}
    
    cache_key = f'weighted_interactions_{user.id}_{days_limit}'
    cached_scores = cache.get(cache_key)
    
    if cached_scores is not None:
        return cached_scores
    
    # Define the cutoff date for recent interactions
    cutoff_date = timezone.now() - timedelta(days=days_limit)
    
    # Get all user interactions within the time period
    interactions = RecipeInteraction.objects.filter(
        user=user,
        timestamp__gte=cutoff_date
    ).values('recipe_id', 'interaction_type', 'timestamp')
    
    # Define weights for different interaction types
    interaction_weights = {
        'favorite': 5.0,
        'cook': 3.0,
        'view': 1.0
    }
    
    # Calculate weighted score for each recipe
    recipe_scores = {}
    
    for interaction in interactions:
        recipe_id = interaction['recipe_id']
        interaction_type = interaction['interaction_type']
        
        # Calculate days since interaction (for time decay)
        days_old = (timezone.now() - interaction['timestamp']).days
        time_factor = max(0, (days_limit - days_old) / days_limit)
        
        # Calculate score for this interaction
        weight = interaction_weights.get(interaction_type, 1.0)
        score = weight * (0.5 + 0.5 * time_factor)  # Base weight + recency boost
        
        # Add to recipe's total score
        if recipe_id in recipe_scores:
            recipe_scores[recipe_id] += score
        else:
            recipe_scores[recipe_id] = score
    
    # Cache the results
    cache.set(cache_key, recipe_scores, 30 * 60)  # 30 minutes
    
    return recipe_scores

def get_interaction_based_recommendations(user, max_results=10):
    """Get recommendations based on all user interactions, not just favorites"""
    if not user.is_authenticated:
        return Recipe.objects.none()
    
    cache_key = f'interaction_recommendations_{user.id}_{max_results}'
    cached_recommendations = cache.get(cache_key)
    
    if cached_recommendations is not None:
        return Recipe.objects.filter(recipe_id__in=cached_recommendations)
    
    # Get weighted interaction scores
    recipe_scores = get_weighted_user_interactions(user)
    
    if not recipe_scores:
        # If no interactions, return popular recipes
        popular_recipes = Recipe.objects.annotate(
            save_count=Count('saved_instances')
        ).order_by('-save_count')[:max_results]
        
        # Cache the fallback results too
        cache.set(
            cache_key, 
            [recipe.recipe_id for recipe in popular_recipes], 
            USER_RECOMMENDATIONS_TTL
        )
        
        return popular_recipes
    
    # Sort recipes by score and take top N for finding similar recipes
    top_interacted_recipes = sorted(
        recipe_scores.items(), 
        key=lambda item: item[1], 
        reverse=True
    )[:5]  # Consider top 5 interacted recipes
    
    # Find similar recipes for each top interacted recipe
    recommended_recipe_ids = set()
    for recipe_id, _ in top_interacted_recipes:
        try:
            similar_recipes = find_similar_recipes(recipe_id, top_n=3)
            recommended_recipe_ids.update(similar_recipes)
        except Exception as e:
            # Log the error but continue with other recipes
            print(f"Error finding similar recipes for {recipe_id}: {str(e)}")
            continue
    
    # Add the top interacted recipes themselves as potential recommendations
    for recipe_id, _ in top_interacted_recipes:
        recommended_recipe_ids.add(recipe_id)
    
    # Get user's dietary preferences
    preferences = get_user_dietary_preferences(user)
    
    # Get the actual recipe objects - limit before expensive filtering
    recommended_recipes = Recipe.objects.filter(recipe_id__in=recommended_recipe_ids)
    
    # Filter by dietary preferences
    if preferences:
        recommended_recipes = filter_by_dietary_preferences(recommended_recipes, preferences)
    
    # Cache the results
    result_recipes = list(recommended_recipes[:max_results])
    result_ids = [recipe.recipe_id for recipe in result_recipes]
    cache.set(cache_key, result_ids, USER_RECOMMENDATIONS_TTL)
    
    # Limit to max_results
    return recommended_recipes[:max_results]

def add_diversity(recipes, max_results=12):
    """Ensure diversity in recommendation results"""
    final_recommendations = []
    # Track recipe categories to ensure diversity
    categories_seen = set()
    recipe_list = list(recipes)  # Convert queryset to list if it's not already
    
    # First pass: extract categories from recipes
    for recipe in recipe_list:
        # Extract a diversity key - using first dietary tag as a category
        diversity_key = recipe.dietary_tags[0] if recipe.dietary_tags else None
        
        # If we haven't seen this category or the recipe doesn't have a category
        if not diversity_key or diversity_key not in categories_seen:
            final_recommendations.append(recipe)
            if diversity_key:
                categories_seen.add(diversity_key)
        
        # If we have enough diverse recommendations, break
        if len(final_recommendations) >= max_results:
            break
    
    # Second pass: fill remaining slots with recipes regardless of diversity
    if len(final_recommendations) < max_results:
        remaining_slots = max_results - len(final_recommendations)
        already_added = {rec.recipe_id for rec in final_recommendations}
        
        for recipe in recipe_list:
            if recipe.recipe_id not in already_added:
                final_recommendations.append(recipe)
                already_added.add(recipe.recipe_id)
                remaining_slots -= 1
                
            if remaining_slots <= 0:
                break
    
    return final_recommendations

def get_personalized_recommendations(user, max_results=12):
    """Get personalized recipe recommendations using multiple strategies with caching"""
    # Try to get from cache first
    cache_key = f'personalized_recommendations_{user.id}_{max_results}'
    cached_recommendations = cache.get(cache_key)
    
    if cached_recommendations is not None:
        return Recipe.objects.filter(recipe_id__in=cached_recommendations)
    
    # Get recommendations from different sources
    interaction_recs = list(get_interaction_based_recommendations(user, max_results=max_results//2))
    content_recs = list(get_content_based_recommendations(user, max_results=max_results//2))
    
    # Combine results (removing duplicates)
    all_recs = []
    seen_ids = set()
    
    # Alternate between recommendation sources for diversity
    for i in range(max(len(interaction_recs), len(content_recs))):
        if i < len(interaction_recs) and interaction_recs[i].recipe_id not in seen_ids:
            all_recs.append(interaction_recs[i])
            seen_ids.add(interaction_recs[i].recipe_id)
            
        if i < len(content_recs) and content_recs[i].recipe_id not in seen_ids:
            all_recs.append(content_recs[i])
            seen_ids.add(content_recs[i].recipe_id)
            
        if len(all_recs) >= max_results:
            break
    
    # Add popular recipes if needed
    if len(all_recs) < max_results:
        # Get user's dietary preferences
        preferences = get_user_dietary_preferences(user)
        
        # Get popular recipes
        popular_recipes = Recipe.objects.annotate(
            save_count=Count('saved_instances')
        ).order_by('-save_count')
        
        # Filter by dietary preferences
        if preferences:
            popular_recipes = filter_by_dietary_preferences(popular_recipes, preferences)
        
        # Filter out recipes we already have
        for recipe in popular_recipes:
            if recipe.recipe_id not in seen_ids and len(all_recs) < max_results:
                all_recs.append(recipe)
                seen_ids.add(recipe.recipe_id)
    
    # Add diversity to final recommendations
    all_recs = add_diversity(all_recs, max_results)
    
    # Cache the final recommendations
    final_recs = all_recs[:max_results]
    cache.set(
        cache_key, 
        [recipe.recipe_id for recipe in final_recs], 
        USER_RECOMMENDATIONS_TTL
    )
    
    return final_recs

# Function to invalidate all recommendation caches for a user
def invalidate_user_recommendations(user_id):
    """Invalidate all recommendation caches for a specific user"""
    pattern_list = [
        f'user_preferences_{user_id}',
        f'user_favorite_ingredients_{user_id}',
        f'content_recommendations_{user_id}_',
        f'interaction_recommendations_{user_id}_',
        f'personalized_recommendations_{user_id}_',
        f'weighted_interactions_{user_id}_',
        f'user_interactions_{user_id}_'
    ]
    
    for pattern in pattern_list:
        # In a real implementation, you would use cache.delete_pattern or similar
        # For Django's default cache, you might need to implement this differently
        cache.delete(pattern)
        
    return True