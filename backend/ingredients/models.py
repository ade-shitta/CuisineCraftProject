from django.db import models
from django.conf import settings

# Create your models here.

class Ingredient(models.Model):
    ingredient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserIngredient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="user_ingredient_entries"
    )

    class Meta:
        unique_together = (("user", "ingredient"),)

    def __str__(self):
        return f"{self.user.username} - {self.ingredient.name}"
