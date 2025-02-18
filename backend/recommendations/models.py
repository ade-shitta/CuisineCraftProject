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
