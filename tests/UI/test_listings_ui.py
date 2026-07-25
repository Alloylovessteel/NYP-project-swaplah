"""End-to-end UI tests for SwapLah listings using Selenium."""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_student_can_create_listing(driver):
    """
    Test Case: End-to-end user journey.
    1. Logs in via the real login page.
    2. Navigates to create listing.
    3. Publishes a new item and verifies redirection.
    """
    wait = WebDriverWait(driver, 10)

    # 1. ARRANGE: Go to the Login Page
    driver.get("http://localhost:5000/login")

    # 2. ACT: Log in using the test account credentials
    wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("254573S@mymail.nyp.edu.sg")
    driver.find_element(By.ID, "password").send_keys("password123")
    
    # Click the Sign In button
    driver.find_element(By.ID, "loginBtn").click()

    # Wait until redirected to profile or marketplace after login
    wait.until(EC.url_contains("/profile"))

    # 3. ACT: Navigate to Create Listing page
    driver.get("http://localhost:5000/create-listing")

    # Fill out the listing form
    wait.until(EC.presence_of_element_located((By.ID, "title"))).send_keys("UI Test Textbook")
    driver.find_element(By.ID, "description").send_keys("Automated browser test description")
    driver.find_element(By.ID, "price").send_keys("25.00")
    driver.find_element(By.ID, "image_url").send_keys("https://images.unsplash.com/photo-1532012197367-6849412a57ce?w=400")

    # Click submit
    submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-btn")))
    submit_btn.click()

    # 4. ASSERT: Verify we are redirected to the marketplace
    wait.until(EC.url_contains("/marketplace"))
    assert "marketplace" in driver.current_url

def test_student_can_search_marketplace(driver):
    """
    Test Case: UI Search flow.
    Verifies that typing a keyword in the marketplace filters the items.
    """
    wait = WebDriverWait(driver, 10)
    driver.get("http://localhost:5000/marketplace")

    search_input = wait.until(EC.presence_of_element_located((By.ID, "searchInput")))
    search_input.send_keys("Physics")
    
    search_btn = driver.find_element(By.ID, "searchBtn")
    search_btn.click()

    # Wait for the container to update with results
    time.sleep(1) 
    container = driver.find_element(By.ID, "listingsContainer")
    assert "Physics" in container.text

def test_student_can_navigate_to_detail_page(driver):
    """
    Test Case: UI Navigation flow.
    Verifies that clicking 'View Details' opens the correct item detail page and loads seller info.
    """
    wait = WebDriverWait(driver, 10)
    driver.get("http://localhost:5000/marketplace")

    # Click the first 'View Details' button available on a card
    view_details_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#listingsContainer .btn-outline-primary")))
    view_details_btn.click()

    # Verify we landed on a listings detail URL
    wait.until(EC.url_contains("/listings/"))
    assert "/listings/" in driver.current_url

    # FIX: Explicitly wait for JavaScript to finish fetching and render "Contact Seller"
    wait.until(EC.text_to_be_present_in_element((By.ID, "detailContainer"), "Contact Seller"))
    
    assert "Contact Seller" in driver.page_source