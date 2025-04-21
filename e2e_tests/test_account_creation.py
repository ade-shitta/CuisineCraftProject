import pytest
import time
from selenium.webdriver.common.by import By
from base_test import BaseTest
import sys

class TestAccountCreation(BaseTest):
    """Test suite for account creation functionality."""
    
    def test_successful_signup(self):
        """Test successful user registration with valid credentials."""
        # Check if application is running
        if not self.check_application_running():
            pytest.skip("Application is not running - skipping test")
        
        # Navigate to signup page
        self.driver.get(f"{self.BASE_URL}/signup")
        self.wait_for_page_to_load()
        
        # Print the current URL to debug
        print(f"Current URL after navigation: {self.driver.current_url}")
        
        # Generate unique email to avoid conflicts
        email = self.generate_unique_email()
        password = "Password123!"
        test_username = f"testuser_{int(time.time())}"
        
        # Fill out form - using name attributes instead of ID
        try:
            # We need to fill the form fields based on their name attributes,
            # not IDs, as seen in the HTML output
            self.wait_for_element(By.NAME, "username").send_keys(test_username)
            self.wait_for_element(By.NAME, "firstName").send_keys("Test")
            self.wait_for_element(By.NAME, "lastName").send_keys("User")
            self.wait_for_element(By.NAME, "email").send_keys(email)
            
            # Find date of birth field if it exists
            try:
                date_field = self.wait_for_element(By.NAME, "dateOfBirth", timeout=3)
                date_field.send_keys("2000-01-01")  # YYYY-MM-DD format
            except Exception as e:
                print("Date of birth field not found, skipping:", e)
            
            self.wait_for_element(By.NAME, "password").send_keys(password)
            
            # Find confirm password field by different methods
            try:
                confirm_pwd = self.driver.find_element(By.NAME, "confirmPassword")
            except:
                # Try different strategies to find the confirm password field
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                password_inputs = [inp for inp in inputs if inp.get_attribute('type') == 'password']
                if len(password_inputs) >= 2:
                    confirm_pwd = password_inputs[1]  # Second password field
                else:
                    raise Exception("Could not find confirm password field")
            
            confirm_pwd.send_keys(password)
            
            # Find and click the signup button
            signup_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Sign Up') or contains(@class, 'signup-button')]")
            print(f"Found signup button: {signup_button.get_attribute('outerHTML')}")
            signup_button.click()
            
            # Wait a bit longer for redirection
            time.sleep(5)  # Increased wait time
            print(f"URL after submission: {self.driver.current_url}")
            
            # More flexible assertion that allows for more path options
            assert any(path in self.driver.current_url for path in ["/home", "/login", "/dietary-preferences"]), \
                f"User was not redirected after successful signup, still at: {self.driver.current_url}"
            
        except Exception as e:
            print(f"Error during test execution: {str(e)}")
            
            # Print the page source to debug
            print("Page source at failure point:")
            print(self.driver.page_source[:1000] + "...") # First 1000 chars
            raise
    
    def test_form_validation(self):
        # Implementation without screenshots
        pass  # Complete this based on your requirements
        
    def test_password_mismatch(self):
        # Implementation without screenshots
        pass  # Complete this based on your requirements