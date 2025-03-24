from django.db import models
from django.conf import settings

# Create your models here.

class DietaryPreference(models.Model):
    pref_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dietary_preferences"
    )
    restriction_type = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.username}: {self.restriction_type}"

class RecipeInteraction(models.Model):
    """Track user interactions with recipes for recommendation purposes"""
    INTERACTION_TYPES = [
        ('view', 'Viewed'),
        ('favorite', 'Favorited'),
        ('cook', 'Cooked'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipe_interactions"
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name="user_interactions"
    )
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.interaction_type} {self.recipe.title}"
