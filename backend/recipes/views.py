from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Recipe, SavedRecipe

# Create your views here.

def recipe_list(request):
    # Get all recipes ordered by title
    all_recipes = Recipe.objects.all().order_by('title')
    
    # Set up pagination - 12 recipes per page (3 rows of 4 in grid)
    paginator = Paginator(all_recipes, 12)  # Show 12 recipes per page
    
    # Get the page number from the request
    page_number = request.GET.get('page', 1)
    
    # Get the Page object for the requested page
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'recipes/recipe_list.html', {
        'recipes': page_obj,
        'page_obj': page_obj,  # Send the page object for pagination controls
    })

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

@login_required
def save_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    # Check if the recipe is already saved to prevent duplicates
    SavedRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    return redirect('recipe_detail', recipe_id=recipe_id)