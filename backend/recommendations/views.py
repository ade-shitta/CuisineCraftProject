from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DietaryPreference
from .forms import DietaryPreferenceForm

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
