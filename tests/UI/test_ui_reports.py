"""UI tests for Reporting & Administration."""

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
    """Create Chrome driver."""

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


def admin_login(driver):
    """Login as administrator."""

    driver.get(f"{BASE_URL}/admin/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.find_element(
        By.ID,
        "email"
    ).send_keys("253817B@mymail.nyp.edu.sg")

    driver.find_element(
        By.ID,
        "password"
    ).send_keys("password123")

    driver.execute_script("doLogin()")

    wait.until(
        EC.url_contains("/admin/reports")
    )


# --------------------------------------------------
# TC03
# View Submitted Reports
# --------------------------------------------------

def test_reports_page_loads(driver):

    admin_login(driver)

    driver.get(f"{BASE_URL}/admin/reports")

    wait = WebDriverWait(driver, 10)

    container = wait.until(
        EC.presence_of_element_located(
            (By.ID, "reportsContainer")
        )
    )

    assert container.is_displayed()
    assert "Reported Listings" in driver.page_source


# --------------------------------------------------
# TC04
# View User Accounts
# --------------------------------------------------

def test_users_page_loads(driver):

    admin_login(driver)

    driver.get(f"{BASE_URL}/admin/users")

    wait = WebDriverWait(driver, 10)

    container = wait.until(
        EC.presence_of_element_located(
            (By.ID, "usersContainer")
        )
    )

    assert container.is_displayed()
    assert "User Accounts" in driver.page_source


# --------------------------------------------------
# TC05
# Suspend User Account
# --------------------------------------------------

def test_suspend_button_exists(driver):

    admin_login(driver)

    driver.get(f"{BASE_URL}/admin/users")

    wait = WebDriverWait(driver, 10)

    suspend_button = wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "suspend-btn")
        )
    )

    assert suspend_button.is_displayed()
    assert suspend_button.text == "Suspend"


# --------------------------------------------------
# TC06
# Unsuspend User Account
# --------------------------------------------------

def test_unsuspend_button_exists(driver):

    admin_login(driver)

    driver.get(f"{BASE_URL}/admin/users")

    wait = WebDriverWait(driver, 10)

    # Suspend the first active user.
    suspend_button = wait.until(
        EC.element_to_be_clickable(
            (By.CLASS_NAME, "suspend-btn")
        )
    )

    suspend_button.click()

    # After reload, an Unsuspend button should appear.
    wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "unsuspend-btn")
        )
    )

    unsuspend_button = driver.find_element(
        By.CLASS_NAME,
        "unsuspend-btn"
    )

    assert unsuspend_button.is_displayed()
    assert unsuspend_button.text == "Unsuspend"


# --------------------------------------------------
# Additional UI Test
# Student cannot access Reports page
# --------------------------------------------------

def test_student_cannot_access_reports(driver):

    driver.get(f"{BASE_URL}/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.find_element(
        By.ID,
        "email"
    ).send_keys("254573S@mymail.nyp.edu.sg")

    driver.find_element(
        By.ID,
        "password"
    ).send_keys("password123")

    driver.execute_script("doLogin()")

    driver.get(f"{BASE_URL}/admin/reports")

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "Forbidden" in driver.page_source or "Unauthorized" in driver.page_source


# --------------------------------------------------
# Additional UI Test
# Student cannot access User Management
# --------------------------------------------------

def test_student_cannot_access_users(driver):

    driver.get(f"{BASE_URL}/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.find_element(
        By.ID,
        "email"
    ).send_keys("254573S@mymail.nyp.edu.sg")

    driver.find_element(
        By.ID,
        "password"
    ).send_keys("password123")

    driver.execute_script("doLogin()")

    driver.get(f"{BASE_URL}/admin/users")

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "Forbidden" in driver.page_source or "Unauthorized" in driver.page_source