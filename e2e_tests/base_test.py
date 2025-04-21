import time
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By

class BaseTest:
    """Base class for all E2E tests with common functionality."""
    
    # Change this to match your actual app URL
    BASE_URL = "http://localhost:3000"  # Frontend URL
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup webdriver before each test."""
        options = webdriver.ChromeOptions()
        
        # Uncomment for headless testing
        # options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        # Setup Chrome webdriver
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Setup
        yield
        
        # Teardown
        self.driver.quit()
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be clickable."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        except TimeoutException:
            # Print debug info when element not found
            print(f"\nFailed to find element: {by}={value}")
            print(f"Current URL: {self.driver.current_url}")
            print("Page source preview:")
            print(self.driver.page_source[:1000] + "...")  # First 1000 chars
            print("\nTrying to locate with more flexible selector...")
            
            # Try to find any form fields that might be relevant
            if by == By.ID and ("name" in value.lower() or "username" in value.lower()):
                elements = self.driver.find_elements(By.XPATH, 
                    "//input[contains(@id, 'name') or contains(@name, 'name') or contains(@placeholder, 'name')]")
                if elements:
                    print(f"Found potential name field with different selector: {elements[0].get_attribute('outerHTML')}")
                    return elements[0]
                    
            elif by == By.ID and "email" in value.lower():
                elements = self.driver.find_elements(By.XPATH, 
                    "//input[contains(@id, 'email') or contains(@name, 'email') or contains(@placeholder, 'email') or @type='email']")
                if elements:
                    print(f"Found potential email field with different selector: {elements[0].get_attribute('outerHTML')}")
                    return elements[0]
                    
            elif by == By.ID and "password" in value.lower():
                elements = self.driver.find_elements(By.XPATH, 
                    "//input[contains(@id, 'password') or contains(@name, 'password') or @type='password']")
                if elements:
                    print(f"Found potential password field with different selector: {elements[0].get_attribute('outerHTML')}")
                    return elements[0]
                    
            elif by == By.XPATH and "Sign Up" in value:
                elements = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Sign Up') or contains(text(), 'Signup') or contains(text(), 'Register')]")
                if elements:
                    print(f"Found potential signup button with different selector: {elements[0].get_attribute('outerHTML')}")
                    return elements[0]
                    
            # Re-raise the exception if we couldn't find a suitable alternative
            raise
    
    def wait_for_visibility(self, by, value, timeout=10):
        """Wait for element to be visible."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
        except TimeoutException:
            print(f"\nFailed to find visible element: {by}={value}")
            print(f"Current URL: {self.driver.current_url}")
            raise
        
    def is_element_present(self, by, value, timeout=5):
        """Check if element is present."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False
            
    def generate_unique_email(self):
        """Generate a unique email for test accounts."""
        timestamp = int(time.time())
        return f"test_user_{timestamp}@example.com"
    
    def wait_for_page_to_load(self, timeout=10):
        """Wait for page to fully load."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            print("Page load timed out - continuing anyway")
    
    def check_application_running(self):
        """Check if the application is running."""
        try:
            self.driver.get(self.BASE_URL)
            self.wait_for_page_to_load()
            return True
        except WebDriverException:
            print(f"\nERROR: Application does not appear to be running at {self.BASE_URL}")
            print("Please make sure your application is running before executing tests.")
            return False