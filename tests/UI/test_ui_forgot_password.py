"""UI test: Forgot password flow."""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture
def driver():
    """Set up headless Chrome driver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    yield driver
    driver.quit()


def test_forgot_password_page_loads(driver):
    """Test that the forgot password page loads correctly."""
    driver.get(f"{BASE_URL}/forgot-password")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "email")))
    assert "SwapLah" in driver.title
    assert driver.find_element(By.ID, "email").is_displayed()


def test_forgot_password_with_invalid_email_shows_error(driver):
    """Test that unregistered email shows error."""
    driver.get(f"{BASE_URL}/forgot-password")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "email")))

    driver.find_element(By.ID, "email").send_keys("notregistered@nyp.edu.sg")
    driver.execute_script("doForgotPassword()")

    wait.until(EC.visibility_of_element_located((By.ID, "error-msg")))
    error = driver.find_element(By.ID, "error-msg")
    assert error.is_displayed()