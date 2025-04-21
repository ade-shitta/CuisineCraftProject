import pytest
import time
from selenium.webdriver.common.by import By
from base_test import BaseTest

class TestFavorites(BaseTest):
    """Test suite for favorites functionality."""
    
    @pytest.fixture(autouse=True)
    def login_first(self, setup):
        """Login before each test in this class."""
        self.driver.get(f"{self.BASE_URL}/login")
        
        try:
            # Update selectors to use NAME instead of ID
            self.wait_for_element(By.NAME, "username").send_keys("Tester")
            self.wait_for_element(By.NAME, "password").send_keys("bigboi21")
            
            # Find and click login button with more flexible selector
            login_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Log In') or contains(text(), 'Login') or contains(@class, 'login-button')]")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(2)
        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise
    
    def test_add_favorites(self, setup):
        """Test adding a recipe to favorites."""
        # Navigate to recipes page
        self.driver.get(f"{self.BASE_URL}/recipes")
        
        # Wait for recipes to load
        recipe_container = self.wait_for_visibility(By.XPATH, "//div[contains(@class, 'grid')]")
        
        # Find the first recipe card
        first_recipe = self.driver.find_element(By.XPATH, "//div[contains(@class, 'grid')]/div[1]")
        
        # Get recipe name for later verification
        recipe_name_element = first_recipe.find_element(By.XPATH, 
            ".//p | .//div[contains(@class, 'text-center')] | .//span | .//h3")
        recipe_name = recipe_name_element.text
        print(f"Found recipe with name: {recipe_name}")
        
        # Find heart icon/favorite button
        heart_icon = None
        try:
            # Try position-based approach first
            heart_icon = first_recipe.find_element(
                By.XPATH, ".//button[contains(@class, 'absolute') and (contains(@class, 'top') or contains(@class, 'right'))]")
            print("Found heart icon using absolute position selector")
        except Exception:
            # Try SVG button next
            try:
                heart_icon = first_recipe.find_element(By.XPATH, ".//button[.//svg]")
                print("Found heart icon as button with SVG")
            except Exception:
                # Fallback to any button
                buttons = first_recipe.find_elements(By.XPATH, ".//button")
                if buttons:
                    heart_icon = buttons[0]  # Take the first button
                    print(f"Using first available button as heart icon (found {len(buttons)} buttons)")
        
        if not heart_icon:
            raise Exception("Could not find heart/favorite button in recipe card")
        
        # Click the heart icon to favorite
        initial_state = heart_icon.get_attribute('outerHTML')
        heart_icon.click()
        print("Clicked heart icon to add favorite")
        
        # Wait for state update
        time.sleep(2)
        
        # Verify button state changed (visual feedback)
        updated_state = heart_icon.get_attribute('outerHTML')
        if initial_state != updated_state:
            print("Button state changed - favoriting action registered")
        
        # Navigate to favorites page to verify
        self.driver.get(f"{self.BASE_URL}/favorites")
        
        # Wait for favorites page to load
        favorites_header = self.wait_for_visibility(By.XPATH, 
            "//h1[contains(text(), 'Favorites') or contains(text(), 'Favourite')]")
        print(f"On favorites page: {favorites_header.text}")
        
        # Find favorite recipes
        favorite_recipes = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'grid')]/div")
        if not favorite_recipes:
            # Try alternative selectors
            favorite_recipes = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'card')] | //div[contains(@class, 'recipe')]")
        
        # Get recipe names
        favorite_names = []
        for recipe in favorite_recipes:
            try:
                name_elem = recipe.find_element(By.XPATH, 
                    ".//p | .//div[contains(@class, 'text-center')] | .//span | .//h3 | .//div[contains(@class, 'title')]")
                favorite_names.append(name_elem.text)
            except:
                text = recipe.text.strip()
                if text:
                    favorite_names.append(text)
        
        print(f"Favorites found: {favorite_names}")
        
        # Verify our recipe was added to favorites
        assert recipe_name in favorite_names, f"Recipe '{recipe_name}' not found in favorites after adding"
        print(f"✓ Successfully verified '{recipe_name}' was added to favorites")

    def test_remove_favorites(self, setup):
        """Test removing a recipe from favorites."""
        # First add a recipe to favorites
        self.driver.get(f"{self.BASE_URL}/recipes")
        recipe_container = self.wait_for_visibility(By.XPATH, "//div[contains(@class, 'grid')]")
        first_recipe = self.driver.find_element(By.XPATH, "//div[contains(@class, 'grid')]/div[1]")
        
        # Get recipe name
        recipe_name_element = first_recipe.find_element(By.XPATH, 
            ".//p | .//div[contains(@class, 'text-center')] | .//span | .//h3")
        recipe_name = recipe_name_element.text
        print(f"Setup: Adding '{recipe_name}' to favorites first")
        
        # Use the SAME approach as test_add_favorites - this works reliably
        heart_icon = None
        try:
            # Try position-based approach first
            heart_icon = first_recipe.find_element(
                By.XPATH, ".//button[contains(@class, 'absolute') and (contains(@class, 'top') or contains(@class, 'right'))]")
            print("Found heart icon using absolute position selector")
        except Exception:
            # Try SVG button next
            try:
                heart_icon = first_recipe.find_element(By.XPATH, ".//button[.//svg]")
                print("Found heart icon as button with SVG")
            except Exception:
                # Fallback to any button
                buttons = first_recipe.find_elements(By.XPATH, ".//button")
                if buttons:
                    heart_icon = buttons[0]  # Take the first button
                    print(f"Using first available button as heart icon (found {len(buttons)} buttons)")
        
        if not heart_icon:
            raise Exception("Could not find heart/favorite button in recipe card")
        
        # Click the heart icon to favorite
        initial_state = heart_icon.get_attribute('outerHTML')
        heart_icon.click()
        print("Clicked heart icon to add favorite")
        
        # Wait longer for state update
        time.sleep(3)
        
        # Verify button state changed (visual feedback)
        updated_state = heart_icon.get_attribute('outerHTML')
        if initial_state != updated_state:
            print("Button state changed - favoriting action registered")
        else:
            print("WARNING: Button state didn't change after click - favorite might not work")
        
        # Rest of the test continues as before...