from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.conf import settings
from .models import DietaryPreference
from .forms import DietaryPreferenceForm
from .recommendation_engine import get_personalized_recommendations, invalidate_user_recommendations
from recipes.models import Recipe, SavedRecipe
from recipes.api import RecipeSerializer

# API Cache TTL (in seconds)
API_CACHE_TTL = 15 * 60  # 15 minutes

class DietaryPreferenceView(APIView):
    """Get and update user dietary preferences"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's dietary preferences"""
        # Try to get from cache
        cache_key = f'api:dietary_preferences:{request.user.id}'
        cached_response = cache.get(cache_key)
        
        if cached_response is not None:
            return Response(cached_response)
        
        preferences = DietaryPreference.objects.filter(user=request.user).values_list('restriction_type', flat=True)
        
        # Get all available options from the form
        form = DietaryPreferenceForm()
        all_choices = dict(form.fields['dietary_preferences'].choices)
        
        # Format response with both options and user selections
        formatted_choices = [
            {
                'id': choice_id,
                'name': choice_label,
                'isSelected': choice_id in preferences
            }
            for choice_id, choice_label in all_choices.items()
        ]
        
        # Cache the formatted response
        cache.set(cache_key, formatted_choices, API_CACHE_TTL)
        
        return Response(formatted_choices)
    
    def post(self, request):
        """Update user's dietary preferences"""
        preferences = request.data.get('preferences', [])
        
        # Clear existing preferences
        DietaryPreference.objects.filter(user=request.user).delete()
        
        # Add new preferences
        for preference in preferences:
            DietaryPreference.objects.create(
                user=request.user,
                restriction_type=preference
            )
        
        # Invalidate related caches
        cache.delete(f'api:dietary_preferences:{request.user.id}')
        invalidate_user_recommendations(request.user.id)
        
        return Response({'success': True})


class RecommendedRecipesView(APIView):
    """Get personalized recipe recommendations for the user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get recommended recipes based on user preferences and history"""
        # Get the max number of recommendations to return (default: 12)
        max_results = int(request.GET.get('limit', 12))
        
        # Check if we should bypass cache
        refresh = request.GET.get('refresh', 'false').lower() == 'true'
        
        # Check cache for recommendations if not explicitly refreshing
        if not refresh:
            cache_key = f'api:recommended_recipes:{request.user.id}:{max_results}'
            cached_data = cache.get(cache_key)
            
            if cached_data is not None:
                return Response(cached_data)
        
        # Get personalized recommendations
        recommended_recipes = get_personalized_recommendations(request.user, max_results=max_results)
        
        # Add prefetch_related to optimize the serialization process
        recommended_recipes = list(recommended_recipes)
        
        # Serialize the recipes
        serializer = RecipeSerializer(recommended_recipes, many=True, context={'request': request})
        serialized_data = serializer.data
        
        # Cache the serialized data
        cache_key = f'api:recommended_recipes:{request.user.id}:{max_results}'
        cache.set(cache_key, serialized_data, API_CACHE_TTL)
        
        return Response(serialized_data)


class AlmostMatchingRecipesView(APIView):
    """Get recipes that almost match available ingredients, with substitution suggestions"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get the ingredients query and other parameters
        ingredients = request.GET.get('ingredients', '')
        max_missing = int(request.GET.get('max_missing', 2))
        limit = int(request.GET.get('limit', 10))
        
        # Check cache for this specific query
        cache_key = f'api:almost_matching:{request.user.id}:{ingredients}:{max_missing}:{limit}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # Find almost matching recipes
        from recommendations.text_utils import find_almost_matching_recipes, suggest_ingredient_substitutions
        
        almost_matching = find_almost_matching_recipes(
            ingredients,
            limit=limit,
            max_missing=max_missing,
            user=request.user
        )
        
        # Format the response
        results = []
        for item in almost_matching:
            recipe = item['recipe']
            missing = item['missing_ingredients']
            
            # Get substitutions for each missing ingredient
            substitutions = []
            for ingredient in missing:
                subs = suggest_ingredient_substitutions(ingredient)
                if subs:
                    substitutions.append({
                        'ingredient': ingredient,
                        'substitutes': subs
                    })
                else:
                    substitutions.append({
                        'ingredient': ingredient,
                        'substitutes': []
                    })
            
            # Create response object
            results.append({
                'recipe': RecipeSerializer(recipe, context={'request': request}).data,
                'missing_ingredients': missing,
                'substitutions': substitutions,
                'missing_count': len(missing)
            })
        
        # Cache the results
        cache.set(cache_key, results, API_CACHE_TTL)
        
        return Response(results)