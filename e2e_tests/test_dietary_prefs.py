import pytest
import time
from selenium.webdriver.common.by import By
from base_test import BaseTest

class TestDietaryPreferences(BaseTest):
    """Test suite for dietary preferences functionality."""
    
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
        
    def test_update_dietary_preferences(self):
        """Test updating dietary preferences."""
        # Navigate to dietary preferences section
        self.driver.get(f"{self.BASE_URL}/dietary-preferences")
        
        # Wait for dietary preferences page to load
        self.wait_for_visibility(By.XPATH, "//h1[contains(text(), 'Dietary Preferences')]")
        
        # Select dietary preferences using more accurate selectors
        try:
            # Wait for the preferences to load
            time.sleep(1)
            
            # Print all text content within the grid to help with debugging
            grid_items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'grid')]//div")
            for i, item in enumerate(grid_items[:5]):  # Just print the first 5
                print(f"Element {i}: {item.tag_name} - {item.text}")
            
            # Based on the AllergyItem component's structure, we need a more precise selector
            preferences_to_select = ["Vegetarian", "Dairy-Free"]
            
            for preference in preferences_to_select:
                # Look for elements with the preference text anywhere inside
                # Use this technique to find elements that contain the preference name somewhere
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{preference}')]")
                
                if elements:
                    # Click the first clickable parent element
                    for element in elements:
                        try:
                            # Try to find a clickable parent - the AllergyItem component itself
                            parent = element
                            for _ in range(3):  # Try up to 3 levels up
                                if "allergy-item" in parent.get_attribute("class") or parent.tag_name == "div":
                                    parent.click()
                                    print(f"Clicked on {preference} preference")
                                    break
                                parent = parent.find_element(By.XPATH, "..")
                            else:
                                # If loop completes without breaking, click the element itself
                                element.click()
                                print(f"Clicked directly on {preference} preference text")
                        except Exception as e:
                            print(f"Couldn't click on {preference}: {e}")
                            continue
                        break
                else:
                    print(f"Could not find preference element: {preference}")
            
            # Find and click save button - use more specific selectors based on the actual page
            save_button = self.wait_for_element(
                By.XPATH, "//button[contains(text(), 'Save Preferences')]")
            print(f"Found save button: {save_button.text}")
            save_button.click()
            
            # Wait for save to complete and redirect
            time.sleep(3)
            
            # Verify we've been redirected to recipes page
            assert any(path in self.driver.current_url for path in ["/recipes", "/home"]), \
                f"Not redirected after saving preferences. Current URL: {self.driver.current_url}"
            
            print(f"Successfully saved preferences and redirected to: {self.driver.current_url}")
            
        except Exception as e:
            print(f"Error during dietary preferences test: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            
            # In case of failure, try to print the page structure to help diagnose
            try:
                all_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'grid')]/*")
                print("Full page structure:")
                for i, elem in enumerate(all_elements[:10]):  # Print first 10 elements
                    print(f"Element {i}: {elem.tag_name} - {elem.text}")
            except:
                print("Could not print page structure")
                
            raise