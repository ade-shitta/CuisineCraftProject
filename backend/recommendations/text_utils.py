import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from recipes.models import Recipe, RecipeIngredient
from django.db.models import Count

def preprocess_text(text):
    """Clean and normalize text for analysis"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_recipe_text_features(recipe):
    """Extract text features from a recipe"""
    # Get ingredients
    ingredients = " ".join([ri.ingredient.name for ri in recipe.recipe_ingredients.all()])
    
    # Combine with instructions
    recipe_text = f"{recipe.title} {ingredients} {recipe.instructions}"
    return preprocess_text(recipe_text)

def build_recipe_text_corpus():
    """Build corpus of all recipe texts for vectorization"""
    recipes = Recipe.objects.all()
    recipe_texts = []
    recipe_ids = []
    
    for recipe in recipes:
        recipe_texts.append(get_recipe_text_features(recipe))
        recipe_ids.append(recipe.recipe_id)
    
    return recipe_texts, recipe_ids

def create_recipe_vectors():
    """Create TF-IDF vectors for all recipes"""
    recipe_texts, recipe_ids = build_recipe_text_corpus()
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english', min_df=2)
    tfidf_matrix = vectorizer.fit_transform(recipe_texts)
    
    return tfidf_matrix, recipe_ids, vectorizer

def find_similar_recipes(recipe_id, top_n=5):
    """Find recipes similar to the given recipe based on text features"""
    tfidf_matrix, recipe_ids, vectorizer = create_recipe_vectors()
    
    # Find index of the target recipe
    try:
        recipe_idx = recipe_ids.index(recipe_id)
    except ValueError:
        return []
    
    # Compute cosine similarity
    cosine_similarities = cosine_similarity(tfidf_matrix[recipe_idx:recipe_idx+1], tfidf_matrix).flatten()
    
    # Get indices of top similar recipes (excluding the recipe itself)
    similar_indices = cosine_similarities.argsort()[:-top_n-1:-1]
    similar_indices = [idx for idx in similar_indices if idx != recipe_idx]
    
    # Get the recipe IDs
    similar_recipe_ids = [recipe_ids[idx] for idx in similar_indices]
    
    return similar_recipe_ids[:top_n]

def search_by_ingredients(ingredient_query, limit=20, user=None):
    """
    Search for recipes containing specific ingredients, filtered by user dietary preferences
    
    Args:
        ingredient_query (str): Comma-separated list of ingredients to search for
        limit (int): Maximum number of results to return
        user: Optional user object to filter by their dietary preferences
        
    Returns:
        QuerySet of Recipe objects containing the ingredients
    """
    # Split and clean the ingredient query
    if not ingredient_query or ingredient_query.strip() == '':
        recipes = Recipe.objects.all()
    else:
        ingredients = [i.strip().lower() for i in ingredient_query.split(',')]
        
        # Start with all recipes
        all_recipes = Recipe.objects.all()
        matching_recipe_ids = []
        
        # Filter for recipes that contain ALL the specified ingredients
        for recipe in all_recipes:
            recipe_ingredients = set([
                ri.ingredient.name.lower() 
                for ri in recipe.recipe_ingredients.all()
            ])
            
            # Check if all search ingredients are in this recipe
            # Using a more flexible matching logic that handles singular/plural forms
            ingredient_match = True
            for ingredient in ingredients:
                # Check for exact match first
                exact_match = any(ingredient in ingredient_name for ingredient_name in recipe_ingredients)
                
                # If no exact match, try checking for singular/plural forms
                if not exact_match:
                    # Check for singular form (remove trailing 's' if present)
                    singular_form = ingredient[:-1] if ingredient.endswith('s') else ingredient
                    singular_match = any(singular_form in ingredient_name for ingredient_name in recipe_ingredients)
                    
                    # Check for plural form (add 's' if not present)
                    plural_form = ingredient if ingredient.endswith('s') else ingredient + 's'
                    plural_match = any(plural_form in ingredient_name for ingredient_name in recipe_ingredients)
                    
                    # Consider a match if either singular or plural form matches
                    if not (singular_match or plural_match):
                        ingredient_match = False
                        break
                
            if ingredient_match:
                matching_recipe_ids.append(recipe.recipe_id)
        
        # Get recipes with the matching IDs
        recipes = Recipe.objects.filter(recipe_id__in=matching_recipe_ids)
    
    # Filter by user dietary preferences if user is provided
    if user and user.is_authenticated:
        from recommendations.models import DietaryPreference
        
        # Get user dietary preferences
        preferences = list(DietaryPreference.objects.filter(
            user=user
        ).values_list('restriction_type', flat=True))
        
        if preferences:
            # Filter recipes for those matching all preferences
            filtered_recipes = []
            
            for recipe in recipes:
                if all(pref in recipe.dietary_tags for pref in preferences):
                    filtered_recipes.append(recipe.recipe_id)
            
            recipes = recipes.filter(recipe_id__in=filtered_recipes)
    
    return recipes[:limit]