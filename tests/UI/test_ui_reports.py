"""UI tests for Reports page."""

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


def test_reports_page_loads(driver):
    """Reports page loads successfully."""

    driver.get(f"{BASE_URL}/admin/reports")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.ID, "reportsContainer"))
    )

    assert "Reported Listings" in driver.page_source


def test_reports_container_exists(driver):
    """Reports container exists."""

    driver.get(f"{BASE_URL}/admin/reports")

    wait = WebDriverWait(driver, 10)

    container = wait.until(
        EC.presence_of_element_located(
            (By.ID, "reportsContainer")
        )
    )

    assert container.is_displayed()


def test_report_buttons_exist(driver):
    """Report buttons are displayed."""

    driver.get(f"{BASE_URL}/admin/reports")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "delete-listing-btn")
        )
    )

    remove_button = driver.find_element(
        By.CLASS_NAME,
        "delete-listing-btn"
    )

    dismiss_button = driver.find_element(
        By.CLASS_NAME,
        "dismiss-report-btn"
    )

    assert remove_button.is_displayed()
    assert dismiss_button.is_displayed()