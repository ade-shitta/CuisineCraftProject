import pytest
import time
from selenium.webdriver.common.by import By
from base_test import BaseTest

class TestLogin(BaseTest):
    """Test suite for login functionality."""
    
    def test_successful_login(self):
        """Test successful login with valid credentials."""
        # Check if application is running
        if not self.check_application_running():
            pytest.skip("Application is not running - skipping test")
        
        # Navigate to login page
        self.driver.get(f"{self.BASE_URL}/login")
        self.wait_for_page_to_load()
        
        # Print URL for debugging
        print(f"Current URL after navigation: {self.driver.current_url}")
        
        try:
            # Use name attributes instead of ID (based on the actual HTML structure)
            self.wait_for_element(By.NAME, "username").send_keys("testuser@example.com")
            self.wait_for_element(By.NAME, "password").send_keys("Password123!")
            
            # Find and click login button with more flexible selector
            login_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Log In') or contains(text(), 'Login') or contains(@class, 'login-button')]")
            print(f"Found login button: {login_button.get_attribute('outerHTML')}")
            login_button.click()
            
            # Wait for redirection/loading
            time.sleep(3)
            print(f"URL after login: {self.driver.current_url}")
            
            # Verify successful login (check for elements that would only appear when logged in)
            # More flexible selector to find user-specific elements
            assert any([
                self.is_element_present(By.XPATH, "//div[contains(@class, 'user-menu')]"), 
                self.is_element_present(By.XPATH, "//div[contains(@class, 'profile-icon')]"),
                self.is_element_present(By.XPATH, "//*[contains(text(), 'Welcome')]"),
                self.is_element_present(By.XPATH, "//*[contains(@class, 'user-name')]"),
                # Check for redirection to authenticated routes
                "/profile" in self.driver.current_url,
                "/dashboard" in self.driver.current_url,
                "/home" in self.driver.current_url
            ]), "User-specific data not found after login - login may have failed"
            
        except Exception as e:
            print(f"Error during login test: {str(e)}")
            
            # Print page source for debugging
            print("Page source at failure point:")
            print(self.driver.page_source[:1000] + "...")  # First 1000 chars
            raise
            
    def test_failed_login(self):
        """Test login failure with incorrect credentials."""
        # Check if application is running
        if not self.check_application_running():
            pytest.skip("Application is not running - skipping test")
            
        # Navigate to login page
        self.driver.get(f"{self.BASE_URL}/login")
        self.wait_for_page_to_load()
        
        try:
            # Enter invalid credentials using name attributes
            self.wait_for_element(By.NAME, "username").send_keys("wrong@example.com")
            self.wait_for_element(By.NAME, "password").send_keys("WrongPassword!")
            
            # Submit form
            login_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Log In') or contains(text(), 'Login') or contains(@class, 'login-button')]")
            login_button.click()
            
            # Wait for the error message to appear
            time.sleep(1)
            
            # Verify error message with flexible selectors
            assert any([
                self.is_element_present(By.XPATH, "//div[contains(@class, 'error')]"),
                self.is_element_present(By.XPATH, "//*[contains(text(), 'Invalid')]"),
                self.is_element_present(By.XPATH, "//*[contains(text(), 'incorrect')]"),
                self.is_element_present(By.XPATH, "//*[contains(text(), 'failed')]"),
                self.is_element_present(By.XPATH, "//*[contains(@class, 'alert')]")
            ]), "Error message not displayed after failed login"
            
            # Ensure we're still on login page
            assert "/login" in self.driver.current_url, "Not on login page after failed login attempt"
            
        except Exception as e:
            print(f"Error during failed login test: {str(e)}")
            
            # Print page source for debugging
            print("Page source at failure point:")
            print(self.driver.page_source[:1000] + "...")  # First 1000 chars
            raise