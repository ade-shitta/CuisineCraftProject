import pytest
import os
import time
from selenium.webdriver.common.by import By
from base_test import BaseTest
import secrets

class TestProfileEditing(BaseTest):
    """Test suite for user profile editing functionality."""
    
    @pytest.fixture(autouse=True)
    def login_first(self, setup):  # Add setup dependency
        """Login before each test in this class."""
        self.driver.get(f"{self.BASE_URL}/login")
        self.wait_for_page_to_load()
        
        try:
            # Enter valid credentials - use an existing test account
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
    
    def test_edit_profile(self):
        """Test user profile editing."""
        # Navigate to profile page
        self.driver.get(f"{self.BASE_URL}/profile")
        self.wait_for_page_to_load()
        
        try:
            # Find and click edit profile button - use more specific selector based on React app
            edit_button = self.wait_for_element(
                By.XPATH, "//button[contains(text(), 'Edit Profile') or (contains(@class, 'btn') and contains(text(), 'Edit'))]")
            edit_button.click()
            
            # Wait for modal to appear - using the correct structure from React app
            # The React modal doesn't use 'modal' class but has fixed positioning and z-50
            modal = self.wait_for_visibility(
                By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'z-50')]")
            
            # Get a unique username to avoid conflicts
            unique_username = f"testuser_{secrets.token_hex(4)}"
            
            # Find and modify the input fields - using form fields within the modal
            username_field = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'fixed')]//input[@id='username']")
            username_field.clear()
            username_field.send_keys(unique_username)
            
            # Find the save button in the modal and click it
            save_button = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'fixed')]//button[@type='submit']")
            save_button.click()
            
            # Wait for the modal to close and changes to be saved
            time.sleep(2)
            
            # Verify the profile was updated - check if we're still on profile page
            assert "/profile" in self.driver.current_url, "No longer on profile page after edit"
            
            # Optional: Verify the username was updated in the UI
            # This depends on how your UI reflects the changes
            
            print("Profile successfully edited")
            
        except Exception as e:
            print(f"Error during profile editing test: {str(e)}")
            # Print the page source for debugging
            print("Page source at failure point:")
            print(self.driver.page_source[:500] + "...")  # First 500 chars
            raise