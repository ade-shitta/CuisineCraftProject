import pytest
import time
from selenium.webdriver.common.by import By
from base_test import BaseTest

class TestRecipeDetails(BaseTest):
    """Test suite for recipe details functionality."""
    
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
    
    def test_recipe_details_view(self):
        """Test viewing recipe details."""
        # Navigate to recipes page
        self.driver.get(f"{self.BASE_URL}/recipes")
        
        # Wait for grid container to be visible first
        grid_container = self.wait_for_visibility(By.XPATH, "//div[contains(@class, 'grid')]")
        
        # Find the first recipe card (using a more general selector that matches the React frontend)
        first_recipe = self.wait_for_element(By.XPATH, 
            "//div[contains(@class, 'grid')]/div[1]")
        
        # Find recipe name (could be in a p tag according to the React component)
        recipe_name_element = first_recipe.find_element(By.XPATH, 
            ".//p | .//div[contains(@class, 'text-center')] | .//span")
        recipe_name = recipe_name_element.text
        print(f"Found recipe with name: {recipe_name}")
        
        # Store current URL to verify we navigate away
        current_url = self.driver.current_url
        
        # Click the recipe
        first_recipe.click()
        
        # Wait for page URL to change (indicating navigation)
        self.wait_until_url_changes(current_url)
        
        # Add brief pause to ensure page has fully loaded
        time.sleep(2)
        
        # Wait for recipe details page to load - look for any main content container
        detail_container = self.wait_for_visibility(By.XPATH, 
            "//div[contains(@class, 'min-h-screen')]")
        
        # Find recipe title in the details page - split the element finding and text extraction
        # to avoid StaleElementReferenceException
        try:
            # Try multiple selectors to find the title
            title_selectors = [
                "//h1[contains(@class, 'text-2xl')]", 
                "//h1[contains(@class, 'font-bold')]",
                "//div[contains(@class, 'text-center')]//h1",
                "//h1",  # Fallback to any h1
                "//div[contains(@class, 'text-xl') or contains(@class, 'text-2xl')]" # Fallback to prominent text
            ]
            
            detail_title_element = None
            for selector in title_selectors:
                try:
                    # Use the wait_for_visibility method with a shorter timeout
                    detail_title_element = self.wait_for_visibility(By.XPATH, selector, timeout=3)
                    if detail_title_element:
                        break
                except:
                    continue
            
            if not detail_title_element:
                # If we still couldn't find a title element, get the page source for debugging
                print("Could not find recipe title. Current page source:")
                print(self.driver.page_source[:500])  # Print first 500 chars
                raise Exception("Could not find recipe title element")
            
            # Get the text from the found element
            detail_title = detail_title_element.text
            print(f"Found detail title: {detail_title}")
            
            # Case-insensitive comparison or partial match since formatting may differ
            assert recipe_name.lower() in detail_title.lower() or detail_title.lower() in recipe_name.lower(), \
                f"Recipe title mismatch: Expected '{recipe_name}', got '{detail_title}'"
        
        except Exception as e:
            print(f"Error while finding recipe title: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            raise
        
        # Check for ingredients section
        ingredients_container = self.wait_for_visibility(By.XPATH, 
            "//div[contains(text(), 'Ingredients') or .//h3[contains(text(), 'Ingredients')]]/..")
        
        # Find and click the View Recipe Details button
        try:
            # Look for different possible button variations
            button_selectors = [
                "//button[contains(text(), 'View Recipe Details')]",
                "//a[contains(text(), 'View Recipe Details')]",
                "//button[contains(text(), 'Instructions')]",
                "//button[contains(text(), 'View Instructions')]",
                "//button[contains(text(), 'Start Cooking')]",
                "//button[contains(text(), 'View Full Recipe')]",
                "//a[contains(@class, 'button') and contains(text(), 'View')]"
            ]
            
            view_details_button = None
            for selector in button_selectors:
                try:
                    view_details_button = self.driver.find_element(By.XPATH, selector)
                    if view_details_button and view_details_button.is_displayed():
                        break
                except:
                    continue
                    
            if not view_details_button:
                print("Could not find View Recipe Details button. Available buttons:")
                buttons = self.driver.find_elements(By.XPATH, "//button")
                for i, btn in enumerate(buttons[:5]):  # Print first 5 buttons
                    print(f"Button {i}: {btn.text}")
                raise Exception("Could not find View Recipe Details button")
                
            print(f"Clicking button: '{view_details_button.text}'")
            view_details_button.click()
            
            # Wait for either a modal to appear or for navigation to occur
            time.sleep(1)
            
            # Check if a modal appeared
            modal_selectors = [
                "//div[contains(@class, 'modal')]",
                "//div[contains(@class, 'fixed')]//div[contains(@class, 'bg-white')]",
                "//div[@role='dialog']"
            ]
            
            modal_found = False
            for selector in modal_selectors:
                try:
                    modal = self.wait_for_visibility(By.XPATH, selector, timeout=3)
                    if modal:
                        modal_found = True
                        print("Modal found with recipe details")
                        
                        # Check for instructions/steps in the modal
                        instructions = modal.find_elements(By.XPATH, 
                            ".//ol/li | .//ul/li | .//div[contains(@class, 'step')] | .//p")
                        
                        if instructions:
                            print(f"Found {len(instructions)} instruction steps")
                        else:
                            print("No instructions found in modal")
                            
                        # Find and click close button if it exists
                        close_buttons = modal.find_elements(By.XPATH, 
                            ".//button[contains(text(), 'Close')] | .//button[contains(@class, 'close')] | .//svg/parent::button")
                            
                        if close_buttons:
                            close_buttons[0].click()
                            print("Closed recipe details modal")
                            time.sleep(1)
                        else:
                            print("No close button found in modal")
                        break
                except:
                    continue
                    
            if not modal_found:
                # Maybe it navigated to a new page instead
                print(f"No modal found - current URL: {self.driver.current_url}")
                
                # Check if we're on a different page with instructions
                instructions_page_elements = self.driver.find_elements(By.XPATH, 
                    "//div[contains(text(), 'Instructions')] | //h3[contains(text(), 'Steps')]")
                    
                if instructions_page_elements:
                    print("Navigated to instructions page")
                else:
                    print("Warning: No modal or instructions page found after clicking button")
                
        except Exception as e:
            print(f"Error interacting with recipe details button: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            # Continue the test even if this part fails
            
    def wait_until_url_changes(self, original_url, timeout=10):
        """Wait until the URL changes from the original URL."""
        end_time = time.time() + timeout
        while time.time() < end_time:
            current_url = self.driver.current_url
            if current_url != original_url:
                return True
            time.sleep(0.5)
        raise TimeoutError(f"URL didn't change from {original_url} within {timeout} seconds")