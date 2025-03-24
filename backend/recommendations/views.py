from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DietaryPreference, RecipeInteraction
from .forms import DietaryPreferenceForm
from .recommendation_engine import get_personalized_recommendations
from recipes.models import SavedRecipe

@login_required
def preferences(request):
    """View for users to select their dietary preferences."""
    # Get existing preferences for this user
    existing_preferences = DietaryPreference.objects.filter(user=request.user).values_list('restriction_type', flat=True)
    
    if request.method == 'POST':
        form = DietaryPreferenceForm(request.POST)
        if form.is_valid():
            # Delete existing preferences
            DietaryPreference.objects.filter(user=request.user).delete()
            
            # Add new preferences
            for preference in form.cleaned_data['dietary_preferences']:
                DietaryPreference.objects.create(
                    user=request.user,
                    restriction_type=preference
                )
            return redirect('recipe_list')  # Redirect to recipes after saving preferences
    else:
        # Pre-select existing preferences
        form = DietaryPreferenceForm(initial={'dietary_preferences': existing_preferences})
    
    return render(request, 'recommendations/preferences.html', {'form': form})

@login_required
def recommended_recipes(request):
    """View to display personalized recipe recommendations"""
    # Get personalized recommendations
    recommended_recipes = get_personalized_recommendations(request.user)
    
    # Get user's favorite recipe IDs for UI
    favorite_recipe_ids = set(SavedRecipe.objects.filter(user=request.user).values_list('recipe__recipe_id', flat=True))
    
    return render(request, 'recommendations/recommended_recipes.html', {
        'recipes': recommended_recipes,
        'favorite_recipe_ids': favorite_recipe_ids
    })
