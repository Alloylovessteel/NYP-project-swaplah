"""UI test: User registration flow."""
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


def test_register_page_loads(driver):
    """Test that the register page loads correctly."""
    driver.get(f"{BASE_URL}/register")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "student_id")))
    assert "SwapLah" in driver.title
    assert driver.find_element(By.ID, "student_id").is_displayed()
    assert driver.find_element(By.ID, "email").is_displayed()
    assert driver.find_element(By.ID, "password").is_displayed()


def test_register_with_invalid_email_shows_error(driver):
    """Test that non-NYP email shows validation error."""
    driver.get(f"{BASE_URL}/register")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "student_id")))

    driver.find_element(By.ID, "student_id").send_keys("S9999001")
    driver.find_element(By.ID, "first_name").send_keys("Test")
    driver.find_element(By.ID, "last_name").send_keys("User")
    driver.find_element(By.ID, "display_name").send_keys("Test U")
    driver.find_element(By.ID, "email").send_keys("test@gmail.com")
    driver.find_element(By.ID, "contact_number").send_keys("91234567")
    driver.find_element(By.ID, "password").send_keys("Password123!")
    driver.find_element(By.ID, "confirm_password").send_keys("Password123!")

    driver.execute_script("doRegister()")

    wait.until(EC.visibility_of_element_located((By.ID, "error-msg")))
    error = driver.find_element(By.ID, "error-msg")
    assert error.is_displayed()