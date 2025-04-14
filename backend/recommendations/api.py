from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import DietaryPreference
from .forms import DietaryPreferenceForm
from .recommendation_engine import get_personalized_recommendations
from recipes.models import Recipe, SavedRecipe
from recipes.api import RecipeSerializer

class DietaryPreferenceView(APIView):
    """Get and update user dietary preferences"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's dietary preferences"""
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
        
        return Response({'success': True})


class RecommendedRecipesView(APIView):
    """Get personalized recipe recommendations for the user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get recommended recipes based on user preferences and history"""
        # Get the max number of recommendations to return (default: 12)
        max_results = int(request.GET.get('limit', 12))
        
        # Get personalized recommendations
        recommended_recipes = get_personalized_recommendations(request.user, max_results=max_results)
        
        # Serialize the recipes
        serializer = RecipeSerializer(recommended_recipes, many=True, context={'request': request})
        
        return Response(serializer.data)