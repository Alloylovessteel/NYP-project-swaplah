"""Pytest configuration file for UI tests."""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="session")
def driver():
    """Chrome WebDriver for Selenium UI tests (supports headless mode for CI)."""
    os.environ["WDM_LOG_LEVEL"] = "0"
    options = Options()

    # If running inside GitLab CI, enable headless mode automatically
    if os.environ.get("CI"):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
