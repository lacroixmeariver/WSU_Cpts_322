"""Tests for page navigation."""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.fixture
def driver():
    """Establish driver for testing use."""
    driver = webdriver.Firefox()  # opens firefox browser window
    yield driver  # hand driver over to the test
    driver.quit()


def test_index_page_loads(driver):
    """Testing that index page loads."""
    driver.get("http://127.0.0.1:5000")
    assert driver.title != ""
    assert "error" not in driver.page_source.lower()


def test_navbar_links_logged_out(driver):
    """Testing navbar links for logged out users."""
    driver.get("http://127.0.0.1:5000")
    driver.implicitly_wait(0.5)
    nav_bar_links = [
        ("home-nav-link", "/"),
        ("login-nav-link", "/h/auth/login"),
    ]

    for link_text, page_url in nav_bar_links:
        driver.get("http://127.0.0.1:5000")
        driver.implicitly_wait(0.5)
        nav_link = driver.find_element(by=By.ID, value=link_text)
        assert nav_link.is_displayed()
        nav_link.click()
        assert page_url in driver.current_url


def test_user_login(driver):
    """Testing login feature."""
    driver.get("http://127.0.0.1:5000/h/auth/login")
    driver.implicitly_wait(0.5)

    # TODO [Ingrid]: write general login test
    # current test based off test login creds in db
    driver.find_element(by=By.NAME, value="uid").send_keys("test")
    driver.find_element(by=By.NAME, value="pw").send_keys("password")
    sign_in = driver.find_element(by=By.ID, value="sign-in-button")
    sign_in.click()
    driver.implicitly_wait(0.5)
    log_out_button = driver.find_element(by=By.ID, value="log-out-button")
    assert log_out_button.is_displayed()
