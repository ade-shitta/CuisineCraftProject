from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Ingredient, UserIngredient

class IngredientSerializer(serializers.ModelSerializer):
    isTracked = serializers.SerializerMethodField()
    
    class Meta:
        model = Ingredient
        fields = ['ingredient_id', 'name', 'isTracked']
        
    def get_isTracked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserIngredient.objects.filter(user=request.user, ingredient=obj).exists()
        return False

class IngredientListView(APIView):
    """Get all ingredients"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True, context={'request': request})
        return Response(serializer.data)

class IngredientDetailView(APIView):
    """Get a single ingredient by ID"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, ingredient_id):
        ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
        serializer = IngredientSerializer(ingredient, context={'request': request})
        return Response(serializer.data)

class UserIngredientsView(APIView):
    """Get ingredients tracked by the current user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_ingredients = UserIngredient.objects.filter(user=request.user).select_related('ingredient')
        ingredients = [ui.ingredient for ui in user_ingredients]
        serializer = IngredientSerializer(ingredients, many=True, context={'request': request})
        return Response(serializer.data)

class TrackIngredientView(APIView):
    """Track an ingredient for the current user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, ingredient_id):
        ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
        user_ingredient, created = UserIngredient.objects.get_or_create(
            user=request.user,
            ingredient=ingredient
        )
        return Response({'success': True, 'isTracked': True}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class UntrackIngredientView(APIView):
    """Untrack an ingredient for the current user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, ingredient_id):
        ingredient = get_object_or_404(Ingredient, pk=ingredient_id)
        deleted, _ = UserIngredient.objects.filter(user=request.user, ingredient=ingredient).delete()
        return Response({'success': deleted > 0, 'isTracked': False})