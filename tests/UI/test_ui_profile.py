"""UI test: Profile page redirects unauthenticated users."""
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


def test_profile_redirects_when_not_logged_in(driver):
    """Test that profile page redirects to login when not authenticated."""
    driver.get(f"{BASE_URL}/profile")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_contains("/login"))
    assert "/login" in driver.current_url


def test_profile_page_loads_when_logged_in(driver):
    """Test that profile page loads after login via API session."""
    import requests
    session = requests.Session()
    session.post(f"{BASE_URL}/api/register", json={
        "student_id": "S1111111",
        "first_name": "Selenium",
        "last_name": "Test",
        "display_name": "Sel T",
        "email": "selenium@nyp.edu.sg",
        "contact_number": "91111111",
        "password": "TestPass123!"
    })
    res = session.post(f"{BASE_URL}/api/login", json={
        "email": "selenium@nyp.edu.sg",
        "password": "TestPass123!"
    })
    assert res.status_code == 200

    cookies = session.cookies.get_dict()
    driver.get(f"{BASE_URL}/login")
    for name, value in cookies.items():
        driver.add_cookie({"name": name, "value": value})

    driver.get(f"{BASE_URL}/profile")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "student_id")))
    assert driver.find_element(By.ID, "student_id").is_displayed()