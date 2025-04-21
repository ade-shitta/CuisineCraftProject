import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from base_test import BaseTest

class TestRecipeSearch(BaseTest):
    """Test suite for recipe search functionality."""
    
    @pytest.fixture(autouse=True)
    def login_first(self, setup):
        """Login before each test in this class."""
        self.driver.get(f"{self.BASE_URL}/login")
        self.wait_for_page_to_load()
        
        try:
            # Update selectors to use NAME instead of ID
            self.wait_for_element(By.NAME, "username").send_keys("Tester")
            self.wait_for_element(By.NAME, "password").send_keys("bigboi21")
            
            # Click login button
            login_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Log In') or contains(text(), 'Login')]")
            login_button.click()
            
            # Wait for redirection/login to complete
            time.sleep(2)
        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise
    
    def test_search_by_ingredients(self):
        """Test searching for recipes by ingredients."""
        # Navigate directly to the ingredient recommendations page
        self.driver.get(f"{self.BASE_URL}/ingredient-recommendations")
        self.wait_for_page_to_load()
        
        # Enter ingredients into the search input
        ingredients = "chicken, garlic, onion"
        input_field = self.wait_for_element(
            By.XPATH, "//input[@placeholder='Add Your Ingredients Here']")
        input_field.clear()
        input_field.send_keys(ingredients)
        
        # Submit the search form by clicking the Search Recipes button
        search_button = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Search Recipes')]")
        search_button.click()
        
        # Wait for the modal with results to appear
        time.sleep(2)
        
        # Verify that results are shown
        modal = self.wait_for_visibility(
            By.XPATH, "//div[contains(@class, 'fixed') and .//h2[contains(text(), 'Ingredients')]]")
        
        # Check if we have results in either the exact or almost matches tabs
        try:
            # Check the exact matches tab first
            exact_match_tab = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Exact Matches')]")
            exact_match_tab.click()
            
            # See if we have recipes or a no-results message
            recipes_or_message = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'space-y-4')]/*")
            
            assert len(recipes_or_message) > 0, "No content found in exact matches tab"
            
            # Click on the Almost Matches tab to check it too
            almost_match_tab = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Almost Matches')]")
            almost_match_tab.click()
            
            # Check if we have content in this tab as well
            almost_match_content = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'space-y-6')]/*")
            
            # We don't assert here as it's okay if one tab has no results
            
            print(f"Found {len(recipes_or_message)} items in exact matches")
            print(f"Found {len(almost_match_content)} items in almost matches")
            
        except Exception as e:
            print(f"Error during recipe search test: {str(e)}")
            raise
    
    def test_empty_search_error(self):
        """Test error handling for empty ingredient search."""
        # Navigate directly to the ingredient recommendations page
        self.driver.get(f"{self.BASE_URL}/ingredient-recommendations")
        self.wait_for_page_to_load()
        
        # Clear the input field (if there's any text)
        input_field = self.wait_for_element(
            By.XPATH, "//input[@placeholder='Add Your Ingredients Here']")
        input_field.clear()
        
        # Submit the form with empty input
        search_button = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Search Recipes')]")
        search_button.click()
        
        # Verify the form wasn't submitted or shows appropriate feedback
        # If the form validation is client-side, the modal shouldn't appear
        time.sleep(1)
        
        # Make sure we're still on the same page (URL shouldn't change)
        assert "/ingredient-recommendations" in self.driver.current_url, "Page URL changed after empty search"
        
        # Verify no modal is shown or an error message is displayed
        modal_elements = self.driver.find_elements(
            By.XPATH, "//div[contains(@class, 'fixed') and .//h2[contains(text(), 'Ingredients')]]")
        
        assert len(modal_elements) == 0, "Modal appeared after empty search submission"
    
    def test_recipe_title_search(self):
        """Test searching for recipes by title/keyword."""
        # Navigate to the main recipes page
        self.driver.get(f"{self.BASE_URL}/recipes")
        self.wait_for_page_to_load()
        
        # Wait for the recipe cards to load first
        self.wait_for_visibility(By.XPATH, "//div[contains(@class, 'grid')]")
        
        # Find the search input field
        search_input = self.wait_for_element(
            By.XPATH, "//input[@placeholder='Search recipes...']")
        
        # Get the initial number of recipes showing
        initial_recipes = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'grid')]/div")
        initial_count = len(initial_recipes)
        print(f"Initial recipe count: {initial_count}")
        
        # Try different search terms until we find one that returns results
        search_terms = ["chicken", "pasta", "beef", "salad", "soup"]
        search_success = False
        
        for search_term in search_terms:
            # Enter the search term
            search_input.clear()
            search_input.send_keys(search_term)
            print(f"Searching for: {search_term}")
            
            # Press Enter to ensure search is triggered
            search_input.send_keys(Keys.ENTER)
            
            # Wait longer for search results to update (React might have debounce)
            time.sleep(3)
            
            # Get the filtered recipes
            filtered_recipes = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'grid')]/div")
            
            if len(filtered_recipes) > 0:
                print(f"Found {len(filtered_recipes)} recipes with search term '{search_term}'")
                search_success = True
                
                # Verify recipe cards are visible
                recipe_cards = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'grid')]/div[contains(@class, 'bg-white')]")
                print(f"Recipe cards found: {len(recipe_cards)}")
                
                # Check for recipe title visibility
                visible_titles = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'grid')]//div[contains(text(), '" + search_term + "') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + search_term.lower() + "')]")
                
                if visible_titles:
                    print(f"Found {len(visible_titles)} titles containing '{search_term}'")
                else:
                    print(f"No visible titles contain '{search_term}', but {len(filtered_recipes)} recipe cards were found")
                
                break
        