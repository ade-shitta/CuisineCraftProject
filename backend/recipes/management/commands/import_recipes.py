from django.core.management.base import BaseCommand
import requests
import time
import os
from django.conf import settings
from pathlib import Path
import urllib.request
from django.core.files import File
from recipes.models import Recipe, RecipeIngredient
from ingredients.models import Ingredient

class Command(BaseCommand):
    help = 'Import recipes from TheMealDB API'

    def add_arguments(self, parser):
        parser.add_argument('--retry', type=int, default=3, 
                          help='Number of retries for failed API requests')
        parser.add_argument('--delay', type=int, default=1,
                          help='Delay in seconds between API requests')
        parser.add_argument('--force', action='store_true',
                          help='Force update existing recipes')

    def handle(self, *args, **options):
        self.retries = options['retry']
        self.delay = options['delay']
        self.force_update = options['force']
        self.media_path = Path(settings.MEDIA_ROOT) / 'recipe_images'
        
        # Create media directory if it doesn't exist
        if not os.path.exists(self.media_path):
            os.makedirs(self.media_path)
            
        self.stdout.write('Starting recipe import from TheMealDB API...')
        
        # First, let's get a list of all available meals by first letter
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        
        for letter in alphabet:
            self.stdout.write(f'Fetching recipes starting with "{letter}"...')
            url = f'https://www.themealdb.com/api/json/v1/1/search.php?f={letter}'
            data = self._make_api_request(url)
            
            if not data or not data.get('meals'):
                self.stdout.write(f'No recipes found for letter "{letter}"')
                continue
                
            for meal_data in data['meals']:
                self._process_meal(meal_data)
                
            # Be nice to the API
            time.sleep(self.delay)
        
        self.stdout.write(self.style.SUCCESS('Recipe import completed!'))
    
    def _make_api_request(self, url):
        """Make API request with retries"""
        attempts = 0
        
        while attempts < self.retries:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()  # Raise exception for 4XX/5XX responses
                return response.json()
            except requests.exceptions.RequestException as e:
                attempts += 1
                if attempts < self.retries:
                    wait_time = self.delay * (2 ** attempts)  # Exponential backoff
                    self.stdout.write(self.style.WARNING(
                        f"API request failed ({e}). Retrying in {wait_time}s... (Attempt {attempts}/{self.retries})"
                    ))
                    time.sleep(wait_time)
                else:
                    self.stdout.write(self.style.ERROR(f"API request failed after {self.retries} attempts: {e}"))
                    return None
    
    def _process_meal(self, meal_data):
        """Process a single meal from the API and save to database"""
        meal_id = meal_data['idMeal']
        title = meal_data['strMeal']
        
        # Enhanced duplicate checking - check by title AND API meal_id
        existing_recipe = Recipe.objects.filter(title=title).first()
        
        if existing_recipe and not self.force_update:
            self.stdout.write(f'Recipe "{title}" already exists, skipping...')
            return existing_recipe
        
        instructions = meal_data['strInstructions']
        image_url = meal_data['strMealThumb'] if meal_data.get('strMealThumb') else None
        
        # Extract dietary tags if available
        dietary_tags = []
        if meal_data.get('strTags'):
            dietary_tags = [tag.strip() for tag in meal_data['strTags'].split(',')]
        
        # Create or update recipe
        if existing_recipe and self.force_update:
            recipe = existing_recipe
            recipe.instructions = instructions
            recipe.dietary_tags = dietary_tags
            recipe.image_url = image_url
            self.stdout.write(f'Updating existing recipe: {title}')
        else:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                dietary_tags=dietary_tags,
                image_url=image_url
            )
            self.stdout.write(f'Creating new recipe: {title}')
        
        # Download and save image
        if image_url:
            image_name = self._download_image(image_url, meal_id)
            
        recipe.save()
        
        # Process ingredients with measurements
        self._process_ingredients(recipe, meal_data)
        
        return recipe
    
    def _download_image(self, image_url, meal_id):
        """Download image from URL and save to media folder"""
        try:
            # Extract file extension from URL
            file_extension = os.path.splitext(image_url)[1] or '.jpg'
            image_name = f'meal_{meal_id}{file_extension}'
            image_path = os.path.join(self.media_path, image_name)
            
            # Download the image
            urllib.request.urlretrieve(image_url, image_path)
            self.stdout.write(f'Downloaded image: {image_name}')
            return image_name
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Failed to download image: {e}'))
            return None
    
    def _process_ingredients(self, recipe, meal_data):
        """
        Process ingredients and measurements from meal data
        """
        # Remove existing ingredients if updating
        if self.force_update:
            RecipeIngredient.objects.filter(recipe=recipe).delete()
        
        # Dictionary to collect ingredients and their measurements
        # This will handle duplicated ingredients in TheMealDB data
        ingredient_dict = {}
                
        # TheMealDB has ingredients from 1-20
        for i in range(1, 21):
            ingredient_name = meal_data.get(f'strIngredient{i}')
            measure = meal_data.get(f'strMeasure{i}')
            
            # Skip if no ingredient or it's empty
            if not ingredient_name or ingredient_name.strip() == '':
                continue
                
            # Clean the ingredient name and measure
            ingredient_name = ingredient_name.strip()
            measure = measure.strip() if measure else ''
            
            # If this ingredient was already seen in this recipe,
            # combine the measurements
            if ingredient_name in ingredient_dict:
                ingredient_dict[ingredient_name]['measure'] += f", {measure}"
            else:
                ingredient_dict[ingredient_name] = {
                    'measure': measure
                }
        
        # Now create recipe ingredients from our collected dictionary
        for ingredient_name, data in ingredient_dict.items():
            # Get or create the ingredient
            ingredient, created = Ingredient.objects.get_or_create(
                name=ingredient_name
            )
            
            # Try to create a new RecipeIngredient relation or update if it exists
            recipe_ingredient, created = RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient,
                defaults={'measurement': data['measure']}
            )
            
            # Update measurement if the relation already existed
            if not created:
                recipe_ingredient.measurement = data['measure']
                recipe_ingredient.save()