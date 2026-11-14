"""UI tests for Administrator Authentication."""

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


# --------------------------------------------------
# TC08
# Administrator logs in successfully
# --------------------------------------------------

def test_admin_login_success(driver):

    driver.get(f"{BASE_URL}/admin/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.find_element(By.ID, "email").send_keys(
        "253817B@mymail.nyp.edu.sg"
    )

    driver.find_element(By.ID, "password").send_keys(
        "password123"
    )

    driver.execute_script("doLogin()")

    wait.until(
        EC.url_contains("/admin/reports")
    )

    assert "/admin/reports" in driver.current_url


# --------------------------------------------------
# TC09
# Invalid administrator password
# --------------------------------------------------

def test_admin_login_invalid_password(driver):

    driver.get(f"{BASE_URL}/admin/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.find_element(By.ID, "email").send_keys(
        "253817B@mymail.nyp.edu.sg"
    )

    driver.find_element(By.ID, "password").send_keys(
        "wrongpassword"
    )

    driver.execute_script("doLogin()")

    wait.until(
        EC.visibility_of_element_located((By.ID, "error-msg"))
    )

    assert driver.find_element(
        By.ID,
        "error-msg"
    ).is_displayed()


# --------------------------------------------------
# TC10
# Student cannot use administrator login
# --------------------------------------------------

def test_student_cannot_use_admin_login(driver):

    driver.get(f"{BASE_URL}/admin/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.find_element(By.ID, "email").send_keys(
        "254573S@mymail.nyp.edu.sg"
    )

    driver.find_element(By.ID, "password").send_keys(
        "password123"
    )

    driver.execute_script("doLogin()")

    wait.until(
        EC.visibility_of_element_located((By.ID, "error-msg"))
    )

    assert driver.find_element(
        By.ID,
        "error-msg"
    ).is_displayed()


# --------------------------------------------------
# TC11
# Administrator cannot use student login
# --------------------------------------------------

def test_admin_cannot_use_student_login(driver):

    driver.get(f"{BASE_URL}/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.find_element(By.ID, "email").send_keys(
        "253817B@mymail.nyp.edu.sg"
    )

    driver.find_element(By.ID, "password").send_keys(
        "password123"
    )

    driver.execute_script("doLogin()")

    wait.until(
        EC.visibility_of_element_located((By.ID, "error-msg"))
    )

    assert driver.find_element(
        By.ID,
        "error-msg"
    ).is_displayed()


# --------------------------------------------------
# TC12
# Reports page requires login
# --------------------------------------------------

def test_reports_require_login(driver):

    driver.get(f"{BASE_URL}/admin/reports")

    assert "Unauthorized" in driver.page_source


# --------------------------------------------------
# TC13
# User Management page requires login
# --------------------------------------------------

def test_users_require_login(driver):

    driver.get(f"{BASE_URL}/admin/users")

    assert "Unauthorized" in driver.page_source

# --------------------------------------------------
# TC14
# Administrator logout
# --------------------------------------------------

def test_admin_logout(driver):

    driver.get(f"{BASE_URL}/admin/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.find_element(By.ID, "email").send_keys(
        "253817B@mymail.nyp.edu.sg"
    )

    driver.find_element(By.ID, "password").send_keys(
        "password123"
    )

    driver.execute_script("doLogin()")

    wait.until(
        EC.url_contains("/admin/reports")
    )

    driver.get(f"{BASE_URL}/admin/logout")

    wait.until(
        EC.url_contains("/admin/login")
    )

    assert "/admin/login" in driver.current_url


# --------------------------------------------------
# Additional UI Test
# Administrator login with empty fields
# --------------------------------------------------

def test_admin_login_empty_fields(driver):

    driver.get(f"{BASE_URL}/admin/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.execute_script("doLogin()")

    wait.until(
        EC.visibility_of_element_located((By.ID, "error-msg"))
    )

    assert driver.find_element(
        By.ID,
        "error-msg"
    ).is_displayed()


# --------------------------------------------------
# Additional UI Test
# Non-existent administrator account
# --------------------------------------------------

def test_admin_login_unknown_account(driver):

    driver.get(f"{BASE_URL}/admin/login")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    driver.find_element(
        By.ID,
        "email"
    ).send_keys("unknown@nyp.edu.sg")

    driver.find_element(
        By.ID,
        "password"
    ).send_keys("password123")

    driver.execute_script("doLogin()")

    wait.until(
        EC.visibility_of_element_located((By.ID, "error-msg"))
    )

    assert driver.find_element(
        By.ID,
        "error-msg"
    ).is_displayed()


# --------------------------------------------------
# Additional UI Test
# Cannot access reports after logout
# --------------------------------------------------

def test_reports_after_logout(driver):

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

    driver.get(f"{BASE_URL}/admin/logout")

    driver.get(f"{BASE_URL}/admin/reports")

    assert (
        "Unauthorized" in driver.page_source
        or "/admin/login" in driver.current_url
    )