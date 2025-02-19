from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Ingredient, UserIngredient

# Create your views here.

def ingredient_list(request):
    """List all available ingredients."""
    ingredients = Ingredient.objects.all()
    return render(request, 'ingredients/ingredient_list.html', {'ingredients': ingredients})

def ingredient_detail(request, ingredient_id):
    """Show details of a specific ingredient."""
    ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
    return render(request, 'ingredients/ingredient_detail.html', {'ingredient': ingredient})

@login_required
def track_ingredient(request, ingredient_id):
    """Track an ingredient for the authenticated user."""
    ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
    # Check if the ingredient is already tracked to prevent duplicates
    UserIngredient.objects.get_or_create(user=request.user, ingredient=ingredient)
    return redirect('ingredient_detail', ingredient_id=ingredient_id)

@login_required
def untrack_ingredient(request, ingredient_id):
    """Untrack an ingredient for the authenticated user."""
    ingredient = get_object_or_404(Ingredient, ingredient_id=ingredient_id)
    # Check if the ingredient is tracked before attempting to delete
    try:
        user_ingredient = UserIngredient.objects.filter(user=request.user, ingredient=ingredient)
        user_ingredient.delete()
    except UserIngredient.DoesNotExist:
        pass
    return redirect('ingredient_detail', ingredient_id=ingredient)