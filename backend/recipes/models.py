from django.db import models
from django.conf import settings

# Create your models here.

class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    dietary_tags = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class SavedRecipe(models.Model):
    saved_recipe_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_recipes"
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        related_name="saved_instances"
    )
    
    def __str__(self):
        return f"{self.user.username} saved {self.recipe.title}"

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients"
    )
    ingredient = models.ForeignKey(
        'ingredients.Ingredient',
        on_delete=models.CASCADE,
        related_name="ingredient_recipes"
    )
    
    class Meta:
        unique_together = (("recipe", "ingredient"),)
    
    def __str__(self):
        return f"{self.recipe.title} includes {self.ingredient.name}"


