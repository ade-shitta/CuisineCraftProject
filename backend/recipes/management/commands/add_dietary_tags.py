from django.core.management.base import BaseCommand
from recipes.models import Recipe, RecipeIngredient
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Add dietary tags to recipes based on their ingredients'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Reset all existing dietary tags before processing')

    def handle(self, *args, **options):
        dietary_tags = [
            'vegetarian', 'vegan-friendly', 'gluten-free', 'halal', 
            'seafood-free', 'dairy-free', 'peanut-free', 'tree-nut-free', 
            'wheat-free', 'sesame-free', 'soy-free', 'sulphite-free', 'egg-free'
        ]
        
        # Define ingredient indicators for each restriction
        non_vegetarian_ingredients = [
            'beef', 'chicken', 'pork', 'lamb', 'turkey', 'bacon', 'ham', 'sausage',
            'meat', 'veal', 'duck', 'goose', 'rabbit', 'venison', 'bison', 'quail',
            'pheasant', 'goat', 'mutton', 'prosciutto', 'salami', 'pepperoni', 'gelatin',
            'anchovy', 'sardine', 'mackerel', 'tuna', 'salmon', 'trout', 'herring',
            'crab', 'lobster', 'shrimp', 'prawn', 'clam', 'mussel', 'oyster', 'scallop',
            'octopus', 'squid', 'cuttlefish', 'escargot', 'snail', 'frog', 'turtle',
            'eel', 'shark', 'whale', 'horse', 'kangaroo', 'crocodile', 'alligator',
            'crayfish', 'crawfish', 'langoustine', 'scampi', 'conch', 'abalone', 'geoduck',
            'crabmeat', 'lobster meat', 'shrimp meat', 'prawn meat', 'clam meat',
            'mussel meat', 'oyster meat', 'scallop meat', 'octopus meat', 'squid meat',
            'cuttlefish meat', 'escargot meat', 'snail meat', 'frog legs', 'turtle meat',
            'eel meat', 'shark meat', 'whale meat', 'horse meat', 'kangaroo meat',
            'bone broth', 'fish sauce', 'worcestershire sauce', 'animal rennet', 'lard', 
            'suet', 'caviar', 'roe', 'fish stock', 'beef stock', 'chicken stock', 'dashi',
            'fish broth', 'beef broth', 'chicken broth', 'bone marrow', 'foie gras',
            'sweetbreads', 'liver', 'kidney', 'heart', 'tongue', 'tripe', 'oxtail'
        ]
        
        non_vegan_ingredients = [
            'milk', 'cream', 'cheese', 'butter', 'yogurt', 'egg', 'honey', 
            'whey', 'casein', 'lactose', 'ghee', 'ice cream', 'mayonnaise',
            'gelatin', 'lard', 'isenglass', 'carmine', 'shellac', 'albumen',
            'beeswax', 'bone char', 'charcoal', 'casein', 'rennet', 'taurine',
            'vitamin D3', 'lanolin', 'collagen', 'elastin', 'keratin', 'silk',
            'royal jelly', 'propolis', 'cochineal', 'confectioner\'s glaze', 
            'E120', 'E542', 'E901', 'E904', 'E471', 'buttermilk', 'custard',
            'quark', 'cottage cheese', 'sour cream'
        ] + non_vegetarian_ingredients
        
        gluten_ingredients = [
            'wheat', 'barley', 'rye', 'malt', 'couscous', 'semolina', 'spelt',
            'farina', 'farro', 'graham flour', 'kamut', 'bulgur', 'durum',
            'triticale', 'flour', 'bread', 'pasta', 'cereal', 'beer', 'ale',
            'lager', 'stout', 'porter', 'malt vinegar', 'soy sauce', 'teriyaki',
            'seitan', 'wheat starch', 'wheat germ', 'wheat bran', 'wheat protein',
            'orzo', 'freekeh', 'matzo', 'fu', 'hing', 'asafoetida', 'udon',
            'soba', 'bread crumbs', 'croutons', 'panko', 'noodles', 'pastry',
            'cake', 'cookie', 'crackers', 'pie crust', 'phyllo', 'biscuit',
            'pretzel', 'tortilla', 'pita'
        ]
        
        non_halal_ingredients = [
            'pork', 'bacon', 'ham', 'gelatin', 'pepperoni', 'alcohol', 'wine',
            'beer', 'rum', 'lard', 'pork gelatin', 'pork fat', 'pork rind',
            'pork sausage', 'pork bacon', 'pork ham', 'pork chop', 'pork loin',
            'pork ribs', 'pork belly', 'pork shoulder', 'pork tenderloin',
            'marsala wine', 'cooking wine', 'sake', 'vodka', 'whiskey', 'brandy',
            'liqueur', 'kirsch', 'animal rennet', 'ethanol', 'gin', 'vermouth',
            'port wine', 'sherry', 'tequila', 'bourbon', 'scotch'
        ]
        
        seafood_ingredients = [
            'fish', 'salmon', 'tuna', 'cod', 'shrimp', 'prawn', 'lobster',
            'crab', 'squid', 'octopus', 'clam', 'mussel', 'oyster', 'scallop',
            'anchovy', 'tilapia', 'halibut', 'mackerel', 'sardine', 'trout',
            'seaweed', 'nori', 'kombu', 'wakame', 'bonito flakes', 'fish sauce', 
            'oyster sauce', 'fish paste', 'shrimp paste', 'surimi', 'caviar', 
            'roe', 'fish stock', 'dashi', 'sushi', 'unagi', 'sea bass', 'catfish',
            'mahi mahi', 'perch', 'snapper', 'flounder', 'haddock', 'sole', 'lox'
        ]
        
        dairy_ingredients = [
            'milk', 'cream', 'cheese', 'butter', 'yogurt', 'whey', 
            'casein', 'lactose', 'ghee', 'ice cream', 'buttermilk',
            'quark', 'cottage cheese', 'ricotta', 'mascarpone', 'kefir',
            'sour cream', 'half and half', 'condensed milk', 'evaporated milk',
            'powdered milk', 'whipping cream', 'creme fraiche', 'buttercream',
            'brie', 'cheddar', 'mozzarella', 'parmesan', 'feta', 'gouda',
            'swiss cheese', 'blue cheese', 'goat cheese', 'paneer', 'milk solids'
        ]
        
        peanut_ingredients = [
            'peanut', 'groundnut', 'peanut butter', 'peanut oil', 'peanut flour',
            'arachis oil', 'monkey nuts', 'satay sauce', 'peanut sauce',
            'beer nuts', 'mixed nuts', 'nut mix'
        ]
        
        tree_nut_ingredients = [
            'almond', 'walnut', 'cashew', 'pecan', 'hazelnut', 'pistachio',
            'macadamia', 'brazil nut', 'pine nut', 'coconut', 'chestnut', 
            'hickory nut', 'beechnut', 'ginkgo nut', 'shea nuts', 'pesto', 
            'marzipan', 'nougat', 'walnut oil', 'almond oil', 'praline', 
            'amaretto', 'frangelico', 'almond milk', 'almond butter',
            'almond extract', 'almond paste', 'cashew butter', 'nutella'
        ]
        
        wheat_ingredients = [
            'wheat', 'flour', 'bread', 'pasta', 'couscous', 'semolina', 
            'bran', 'farina', 'wheat germ', 'cracked wheat', 'freekeh',
            'seitan', 'bulgur', 'panko breadcrumbs', 'filo', 'phyllo',
            'wheat starch', 'wheat noodles', 'udon', 'ramen', 'cake flour',
            'all-purpose flour', 'bread flour', 'pastry flour'
        ]
        
        sesame_ingredients = [
            'sesame', 'tahini', 'sesame oil', 'sesame seed', 'halvah',
            'gomasio', 'sesame salt', 'hummus', 'benne seed', 'sesame paste',
            'sesame seasoning', 'sesame snaps', 'goma'
        ]
        
        soy_ingredients = [
            'soy', 'tofu', 'miso', 'tempeh', 'edamame', 'soya',
            'soy sauce', 'tamari', 'soy lecithin', 'soy protein',
            'soy milk', 'textured vegetable protein', 'tvp', 'okara',
            'yuba', 'natto', 'soy nuts', 'soy flour', 'soy oil',
            'soybean', 'shoyu', 'teriyaki', 'vegetable protein'
        ]
        
        sulphite_ingredients = [
            'wine', 'dried fruit', 'vinegar', 'sulphite', 'sulfite',
            'wine vinegar', 'dried vegetables', 'fruit juice', 'molasses',
            'sauerkraut', 'pickled foods', 'beer', 'cider', 'wine coolers',
            'grape juice', 'bottled lemon juice', 'bottled lime juice',
            'dried apricots', 'dried prunes', 'maraschino cherries'
        ]
        
        egg_ingredients = [
            'egg', 'mayonnaise', 'meringue', 'albumin', 'egg white',
            'egg yolk', 'eggnog', 'egg powder', 'egg substitutes',
            'lecithin', 'livetin', 'lysozyme', 'hollandaise sauce',
            'custard', 'meringue powder', 'surimi', 'caesar dressing',
            'aioli', 'quiche', 'frittata', 'egg noodles', 'egg wash',
            'cake', 'cookie', 'muffin', 'pancake'
        ]
        
        # Process all recipes
        recipes = Recipe.objects.all()
        self.stdout.write(f"Processing {recipes.count()} recipes...")
        
        # Reset dietary tags if requested
        if options['reset']:
            self.stdout.write("Resetting existing dietary tags...")
            for recipe in recipes:
                recipe.dietary_tags = []
                recipe.save()
        
        processed_count = 0
        
        for recipe in recipes:
            # Get all ingredients for this recipe
            recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            ingredient_names = [ri.ingredient.name.lower() for ri in recipe_ingredients]
            ingredient_text = ' '.join(ingredient_names)
            
            # Start with all tags, then remove as needed
            recipe_tags = set(dietary_tags)
            
            # Check vegetarian
            if any(ing in ingredient_text for ing in non_vegetarian_ingredients):
                recipe_tags.discard('vegetarian')
            
            # Check vegan
            if any(ing in ingredient_text for ing in non_vegan_ingredients):
                recipe_tags.discard('vegan-friendly')
            
            # Check gluten-free
            if any(ing in ingredient_text for ing in gluten_ingredients):
                recipe_tags.discard('gluten-free')
            
            # Check halal
            if any(ing in ingredient_text for ing in non_halal_ingredients):
                recipe_tags.discard('halal')
            
            # Check seafood-free
            if any(ing in ingredient_text for ing in seafood_ingredients):
                recipe_tags.discard('seafood-free')
            
            # Check dairy-free
            if any(ing in ingredient_text for ing in dairy_ingredients):
                recipe_tags.discard('dairy-free')
            
            # Check peanut-free
            if any(ing in ingredient_text for ing in peanut_ingredients):
                recipe_tags.discard('peanut-free')
            
            # Check tree-nut-free
            if any(ing in ingredient_text for ing in tree_nut_ingredients):
                recipe_tags.discard('tree-nut-free')
            
            # Check wheat-free
            if any(ing in ingredient_text for ing in wheat_ingredients):
                recipe_tags.discard('wheat-free')
            
            # Check sesame-free
            if any(ing in ingredient_text for ing in sesame_ingredients):
                recipe_tags.discard('sesame-free')
            
            # Check soy-free
            if any(ing in ingredient_text for ing in soy_ingredients):
                recipe_tags.discard('soy-free')
            
            # Check sulphite-free
            if any(ing in ingredient_text for ing in sulphite_ingredients):
                recipe_tags.discard('sulphite-free')
            
            # Check egg-free
            if any(ing in ingredient_text for ing in egg_ingredients):
                recipe_tags.discard('egg-free')
            
            # Update recipe with identified tags
            old_tags = recipe.dietary_tags
            recipe.dietary_tags = list(recipe_tags)
            recipe.save()
            
            processed_count += 1
            if processed_count % 50 == 0:
                self.stdout.write(f"Processed {processed_count} recipes...")
                
        self.stdout.write(self.style.SUCCESS(f"Successfully added dietary tags to {processed_count} recipes!"))