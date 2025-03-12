from django import forms
from .models import DietaryPreference

class DietaryPreferenceForm(forms.Form):
    DIETARY_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('vegan-friendly', 'Vegan-Friendly'),
        ('gluten-free', 'Gluten-Free'),
        ('halal', 'Halal'),
        ('seafood-free', 'Seafood-Free'),
        ('dairy-free', 'Dairy-Free'),
        ('peanut-free', 'Peanut-Free'),
        ('tree-nut-free', 'Tree-Nut-Free'),
        ('wheat-free', 'Wheat-Free'),
        ('sesame-free', 'Sesame-Free'),
        ('soy-free', 'Soy-Free'),
        ('sulphite-free', 'Sulphite-Free'),
        ('egg-free', 'Egg-Free'),
    ]
    
    dietary_preferences = forms.MultipleChoiceField(
        choices=DIETARY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Your Dietary Preferences"
    )