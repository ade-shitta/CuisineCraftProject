from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Recipe, SavedRecipe, RecipeIngredient
from django.shortcuts import get_object_or_404
from django.db.models import Q
from recommendations.models import RecipeInteraction, DietaryPreference
from rest_framework import serializers
from recommendations.recommendation_engine import filter_by_dietary_preferences

class RecipeSerializer(serializers.ModelSerializer):
    isFavorite = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = ['recipe_id', 'title', 'instructions', 'dietary_tags', 'image_url', 'isFavorite', 'ingredients']
    
    def get_isFavorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedRecipe.objects.filter(user=request.user, recipe=obj).exists()
        return False
        
    def get_ingredients(self, obj):
        ingredients = []
        for ri in obj.recipe_ingredients.all():
            ingredients.append({
                'name': ri.ingredient.name,
                'amount': ri.measurement
            })
        return ingredients

class RecipeListView(APIView):
    """Get all recipes"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        recipes = Recipe.objects.all().order_by('title')
        
        # Filter by user's dietary preferences
        # Get user's dietary preferences
        preferences = list(DietaryPreference.objects.filter(
            user=request.user
        ).values_list('restriction_type', flat=True))
        
        # Filter recipes by preferences if the user has any
        if preferences:
            recipes = filter_by_dietary_preferences(recipes, preferences)
        
        serializer = RecipeSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)

class RecipeDetailView(APIView):
    """Get a single recipe by ID"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        
        # Record view interaction
        RecipeInteraction.objects.create(
            user=request.user,
            recipe=recipe,
            interaction_type='view'
        )
        
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data)

class ToggleFavoriteView(APIView):
    """Toggle favorite status for a recipe"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        saved_recipe = SavedRecipe.objects.filter(user=request.user, recipe=recipe).first()
        
        if saved_recipe:
            # If already favorited, remove it
            saved_recipe.delete()
            is_favorite = False
        else:
            # If not favorited, add it
            SavedRecipe.objects.create(user=request.user, recipe=recipe)
            is_favorite = True
            
            # Record favorite interaction
            RecipeInteraction.objects.create(
                user=request.user,
                recipe=recipe,
                interaction_type='favorite'
            )
        
        return Response({'isFavorite': is_favorite})

class FavoriteRecipesView(APIView):
    """Get all favorite recipes for a user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        saved_recipes = SavedRecipe.objects.filter(user=request.user).select_related('recipe')
        recipes = [saved.recipe for saved in saved_recipes]
        
        serializer = RecipeSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)

class RecipeSearchView(APIView):
    """Search for recipes"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.GET.get('query', '')
        
        if query:
            recipes = Recipe.objects.filter(
                Q(title__icontains=query) |
                Q(instructions__icontains=query) |
                Q(dietary_tags__contains=[query])
            ).distinct()
        else:
            recipes = Recipe.objects.all()  # Don't limit here, wait until after filtering
        
        # Filter by user's dietary preferences
        preferences = list(DietaryPreference.objects.filter(
            user=request.user
        ).values_list('restriction_type', flat=True))
        
        # Filter recipes by preferences if the user has any
        if preferences:
            recipes = filter_by_dietary_preferences(recipes, preferences)
        
        # Limit results after filtering
        if not query:
            recipes = recipes[:10]
            
        serializer = RecipeSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)

class MarkRecipeCookedView(APIView):
    """Mark a recipe as cooked by the user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        
        # Record cook interaction
        RecipeInteraction.objects.create(
            user=request.user,
            recipe=recipe,
            interaction_type='cook'
        )
        
        return Response({'success': True})