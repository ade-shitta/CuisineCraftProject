import re
import numpy as np
import pickle
import os
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from recipes.models import Recipe, RecipeIngredient
from django.db.models import Count
from django.core.cache import cache

# Cache keys
TFIDF_MATRIX_CACHE_KEY = 'recipe_tfidf_matrix'
RECIPE_IDS_CACHE_KEY = 'recipe_ids_for_tfidf'
VECTORIZER_CACHE_KEY = 'recipe_tfidf_vectorizer'

# Cache TTL - 24 hours in seconds
CACHE_TTL = 24 * 60 * 60

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

def create_recipe_vectors(force_rebuild=False):
    """
    Create TF-IDF vectors for all recipes with caching
    
    Args:
        force_rebuild (bool): If True, rebuild the vectors even if cached
    """
    # Try to get cached values
    if not force_rebuild:
        tfidf_matrix = cache.get(TFIDF_MATRIX_CACHE_KEY)
        recipe_ids = cache.get(RECIPE_IDS_CACHE_KEY)
        vectorizer = cache.get(VECTORIZER_CACHE_KEY)
        
        if tfidf_matrix is not None and recipe_ids is not None and vectorizer is not None:
            return tfidf_matrix, recipe_ids, vectorizer
    
    # If not cached or forced rebuild, create new vectors
    recipe_texts, recipe_ids = build_recipe_text_corpus()
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english', min_df=2)
    tfidf_matrix = vectorizer.fit_transform(recipe_texts)
    
    # Cache the results
    cache.set(TFIDF_MATRIX_CACHE_KEY, tfidf_matrix, CACHE_TTL)
    cache.set(RECIPE_IDS_CACHE_KEY, recipe_ids, CACHE_TTL)
    cache.set(VECTORIZER_CACHE_KEY, vectorizer, CACHE_TTL)
    
    return tfidf_matrix, recipe_ids, vectorizer

def find_similar_recipes(recipe_id, top_n=5):
    """Find recipes similar to the given recipe based on text features"""
    # Use cached vectors if available
    tfidf_matrix, recipe_ids, vectorizer = create_recipe_vectors()
    
    # Check if this recipe's similarity scores are cached
    similarity_cache_key = f'recipe_similarity_{recipe_id}'
    cached_similar_ids = cache.get(similarity_cache_key)
    
    if cached_similar_ids is not None:
        return cached_similar_ids[:top_n]
    
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
    
    # Cache the results (store more than needed for flexibility in later requests)
    cache.set(similarity_cache_key, similar_recipe_ids, CACHE_TTL)
    
    return similar_recipe_ids[:top_n]

# Function to explicitly rebuild the recommendation vectors
def rebuild_recommendation_vectors():
    """Force rebuild of all recommendation vectors"""
    create_recipe_vectors(force_rebuild=True)
    return True

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

def find_almost_matching_recipes(ingredient_query, limit=10, max_missing=2, user=None):
    """
    Find recipes that almost match the provided ingredients (missing just a few)
    
    Args:
        ingredient_query (str): Comma-separated list of ingredients available
        limit (int): Maximum number of results to return
        max_missing (int): Maximum number of missing ingredients allowed
        user: Optional user object to filter by their dietary preferences
        
    Returns:
        List of dicts with recipe objects and missing ingredients
    """
    # Split and clean the ingredient query
    if not ingredient_query or ingredient_query.strip() == '':
        return []
    
    user_ingredients = [i.strip().lower() for i in ingredient_query.split(',')]
    
    # Cache key for this query
    cache_key = f'almost_matching_recipes:{",".join(sorted(user_ingredients))}:{max_missing}'
    if user and user.is_authenticated:
        cache_key += f':{user.id}'
    
    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Get all recipes
    all_recipes = Recipe.objects.prefetch_related('recipe_ingredients__ingredient')
    
    # Filter by user dietary preferences if applicable
    if user and user.is_authenticated:
        from recommendations.models import DietaryPreference
        preferences = list(DietaryPreference.objects.filter(
            user=user
        ).values_list('restriction_type', flat=True))
        
        if preferences:
            filtered_recipes = []
            for recipe in all_recipes:
                if all(pref in recipe.dietary_tags for pref in preferences):
                    filtered_recipes.append(recipe.recipe_id)
            
            all_recipes = all_recipes.filter(recipe_id__in=filtered_recipes)
    
    almost_matching = []
    
    # Analyze each recipe to find those missing just a few ingredients
    for recipe in all_recipes:
        recipe_ingredients = [ri.ingredient.name.lower() for ri in recipe.recipe_ingredients.all()]
        
        # Find missing ingredients
        missing_ingredients = []
        
        for recipe_ingredient in recipe_ingredients:
            # Check if this ingredient or a similar form is in user's ingredients
            found = False
            
            # Direct match check
            for user_ingredient in user_ingredients:
                if user_ingredient in recipe_ingredient or recipe_ingredient in user_ingredient:
                    found = True
                    break
            
            # Check for singular/plural forms if no direct match
            if not found:
                for user_ingredient in user_ingredients:
                    # Check singular form
                    singular = user_ingredient[:-1] if user_ingredient.endswith('s') else user_ingredient
                    if singular in recipe_ingredient:
                        found = True
                        break
                    
                    # Check plural form
                    plural = user_ingredient if user_ingredient.endswith('s') else user_ingredient + 's'
                    if plural in recipe_ingredient:
                        found = True
                        break
            
            if not found:
                missing_ingredients.append(recipe_ingredient)
        
        # If the number of missing ingredients is within our threshold
        if 0 < len(missing_ingredients) <= max_missing:
            almost_matching.append({
                'recipe': recipe,
                'missing_ingredients': missing_ingredients,
                'missing_count': len(missing_ingredients)
            })
    
    # Sort by number of missing ingredients (ascending)
    almost_matching.sort(key=lambda x: x['missing_count'])
    
    # Limit to requested number
    result = almost_matching[:limit]
    
    # Cache the result
    cache.set(cache_key, result, 60 * 15)  # Cache for 15 minutes
    
    return result

def suggest_ingredient_substitutions(ingredient_name):
    """
    Suggest possible substitutions for a given ingredient
    
    Args:
        ingredient_name (str): Name of the ingredient to find substitutes for
        
    Returns:
        List of potential substitute ingredients
    """
    # Define ingredient categories for more flexible substitution
    ingredient_categories = {
        'oils_and_fats': [
            'butter', 'margarine', 'olive oil', 'vegetable oil', 'coconut oil', 'canola oil',
            'avocado oil', 'sesame oil', 'ghee', 'lard', 'shortening', 'bacon fat'
        ],
        'dairy': [
            'milk', 'heavy cream', 'half and half', 'yogurt', 'greek yogurt', 'sour cream',
            'buttermilk', 'cream cheese', 'cottage cheese', 'ricotta cheese'
        ],
        'plant_milk': [
            'almond milk', 'soy milk', 'oat milk', 'coconut milk', 'rice milk', 
            'cashew milk', 'hemp milk', 'flax milk', 'pea milk'
        ],
        'sweeteners': [
            'sugar', 'brown sugar', 'honey', 'maple syrup', 'agave nectar', 'stevia',
            'corn syrup', 'molasses', 'date syrup', 'coconut sugar', 'monk fruit sweetener'
        ],
        'flours': [
            'all-purpose flour', 'whole wheat flour', 'bread flour', 'cake flour', 'pastry flour',
            'almond flour', 'coconut flour', 'rice flour', 'oat flour', 'corn flour',
            'chickpea flour', 'cassava flour', 'tapioca flour', 'buckwheat flour', 'spelt flour'
        ],
        'grains': [
            'rice', 'quinoa', 'farro', 'barley', 'couscous', 'bulgur wheat', 'millet',
            'polenta', 'oats', 'brown rice', 'wild rice', 'freekeh', 'rice noodles'
        ],
        'proteins': [
            'chicken', 'beef', 'pork', 'turkey', 'fish', 'shrimp', 'tofu', 'tempeh',
            'seitan', 'lentils', 'beans', 'chickpeas', 'eggs', 'textured vegetable protein'
        ],
        'herbs': [
            'basil', 'parsley', 'cilantro', 'mint', 'rosemary', 'thyme', 'sage', 'oregano',
            'dill', 'chives', 'tarragon', 'marjoram', 'bay leaves'
        ],
        'spices': [
            'cinnamon', 'nutmeg', 'cloves', 'allspice', 'cardamom', 'cumin', 'coriander',
            'paprika', 'turmeric', 'ginger', 'black pepper', 'white pepper', 'cayenne pepper',
            'curry powder', 'garam masala', 'five spice powder', 'za\'atar'
        ],
        'vegetables': [
            'onion', 'garlic', 'carrots', 'celery', 'bell peppers', 'tomatoes', 'potatoes',
            'sweet potatoes', 'zucchini', 'eggplant', 'broccoli', 'cauliflower', 'spinach',
            'kale', 'cabbage', 'Brussels sprouts', 'asparagus', 'green beans'
        ],
        'fruits': [
            'apples', 'oranges', 'bananas', 'berries', 'peaches', 'plums', 'nectarines',
            'pears', 'pineapple', 'mango', 'papaya', 'avocado', 'coconut', 'lemon', 'lime'
        ],
        'nuts_and_seeds': [
            'almonds', 'walnuts', 'pecans', 'cashews', 'peanuts', 'hazelnuts', 'pistachios',
            'chia seeds', 'flax seeds', 'sunflower seeds', 'pumpkin seeds', 'pine nuts',
            'sesame seeds', 'hemp seeds'
        ],
        'thickeners': [
            'cornstarch', 'arrowroot', 'tapioca starch', 'potato starch', 'xanthan gum',
            'guar gum', 'gelatin', 'agar agar', 'pectin'
        ],
        'condiments': [
            'ketchup', 'mustard', 'mayonnaise', 'soy sauce', 'tamari', 'coconut aminos',
            'hot sauce', 'sriracha', 'worcestershire sauce', 'fish sauce', 'hoisin sauce',
            'barbecue sauce', 'vinegar', 'lemon juice', 'lime juice'
        ]
    }
    
    # Direct substitution pairs for specific ingredients
    substitution_map = {
        'butter': ['margarine', 'olive oil', 'coconut oil', 'ghee', 'applesauce', 'mashed banana'],
        'milk': ['almond milk', 'soy milk', 'oat milk', 'coconut milk', 'rice milk', 'cashew milk'],
        'cream': ['coconut cream', 'evaporated milk', 'greek yogurt', 'cashew cream', 'silken tofu cream'],
        'eggs': ['applesauce', 'mashed banana', 'flaxseed mixed with water', 'chia seeds mixed with water', 'commercial egg replacer'],
        'flour': ['almond flour', 'coconut flour', 'rice flour', 'oat flour', 'gluten-free flour blend', 'cassava flour'],
        'sugar': ['honey', 'maple syrup', 'stevia', 'agave nectar', 'coconut sugar', 'date sugar', 'monk fruit sweetener'],
        'rice': ['quinoa', 'cauliflower rice', 'bulgur wheat', 'farro', 'barley', 'couscous'],
        'pasta': ['zucchini noodles', 'spaghetti squash', 'rice noodles', 'shirataki noodles', 'lentil pasta', 'chickpea pasta'],
        'bread crumbs': ['crushed crackers', 'rolled oats', 'almond meal', 'cornmeal', 'ground flaxseed', 'crushed cereal'],
        'beef': ['portobello mushrooms', 'lentils', 'seitan', 'plant-based beef', 'jackfruit', 'tofu'],
        'chicken': ['tofu', 'tempeh', 'chickpeas', 'jackfruit', 'seitan', 'cauliflower'],
        'fish': ['tofu', 'tempeh', 'heart of palm', 'chickpeas', 'jackfruit', 'seitan'],
        'cheese': ['nutritional yeast', 'vegan cheese', 'cashew cheese', 'tofu ricotta', 'hummus'],
        'soy sauce': ['tamari', 'coconut aminos', 'liquid aminos', 'worcestershire sauce', 'miso paste mixed with water'],
        'vinegar': ['lemon juice', 'lime juice', 'apple cider vinegar', 'rice vinegar', 'white wine'],
        'wine': ['grape juice', 'broth', 'pomegranate juice', 'cranberry juice', 'stock with a splash of vinegar'],
        'breadcrumbs': ['crushed crackers', 'rolled oats', 'almond meal', 'cornmeal', 'ground flaxseed', 'crushed cereal'],
        'mayonnaise': ['greek yogurt', 'mashed avocado', 'hummus', 'tahini', 'cashew cream', 'silken tofu dressing'],
        'onion': ['shallots', 'leeks', 'green onions', 'onion powder', 'celery', 'fennel bulb'],
        'garlic': ['shallots', 'garlic powder', 'chives', 'asafoetida', 'onion powder'],
        'tomatoes': ['red bell peppers', 'pumpkin', 'carrots', 'roasted red bell peppers', 'sun-dried tomatoes'],
        'tomato paste': ['ketchup', 'tomato sauce reduced', 'sun-dried tomato puree', 'red pepper paste'],
        'broth/stock': ['bouillon cubes with water', 'miso paste with water', 'vegetable juice', 'dashi'],
        'cornstarch': ['arrowroot powder', 'potato starch', 'tapioca starch', 'rice flour', 'all-purpose flour'],
        'baking powder': ['baking soda with cream of tartar', 'self-rising flour', 'whipped egg whites', 'club soda'],
        'chocolate chips': ['cacao nibs', 'carob chips', 'chopped chocolate bar', 'dried fruit bits'],
        'sour cream': ['greek yogurt', 'crème fraîche', 'cottage cheese', 'buttermilk', 'cashew cream'],
        'heavy cream': ['evaporated milk', 'coconut cream', 'silken tofu blended with soy milk', 'cashew cream'],
        'honey': ['maple syrup', 'agave nectar', 'brown rice syrup', 'date syrup', 'molasses', 'corn syrup'],
    }
    
    # Convert to lowercase for comparison
    ingredient_name = ingredient_name.lower()
    
    # Look for direct matches in the substitution map
    for key, substitutes in substitution_map.items():
        if key in ingredient_name or ingredient_name in key:
            return substitutes
    
    # Check for singular/plural forms
    singular = ingredient_name[:-1] if ingredient_name.endswith('s') else ingredient_name
    plural = ingredient_name if ingredient_name.endswith('s') else ingredient_name + 's'
    
    for key, substitutes in substitution_map.items():
        if key == singular or key == plural:
            return substitutes
    
    # If no direct match, try to find the ingredient category
    found_category = None
    for category, ingredients in ingredient_categories.items():
        if ingredient_name in ingredients:
            found_category = category
            break
        
        # Check singular/plural forms in categories too
        if singular in ingredients or plural in ingredients:
            found_category = category
            break
    
    # If we found a category, suggest other ingredients from the same category
    if found_category:
        # Get all ingredients from the category
        category_items = ingredient_categories[found_category]
        
        # Return up to 5 alternatives (excluding the original ingredient)
        substitutes = [item for item in category_items if item != ingredient_name 
                      and item != singular and item != plural][:5]
        
        if substitutes:
            return substitutes
    
    # No direct match found, try prefix matching as a last resort
    for key, substitutes in substitution_map.items():
        if (len(key) >= 3 and key[:3] == ingredient_name[:3]) or \
           (len(ingredient_name) >= 3 and ingredient_name[:3] == key[:3]):
            return substitutes
    
    # Return an empty list if no substitutes found
    return []