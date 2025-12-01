"""Tests for auth navigation."""

import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


@pytest.fixture
def driver():
    """Establish driver for testing use."""
    driver = webdriver.Firefox()  # opens firefox browser window
    yield driver  # hand driver over to the test
    driver.quit()


@pytest.fixture
def test_user():
    """Create a test user for login testing."""
    unique_test_id = str(uuid.uuid4())[:6]  # first 6 chars
    test_pw = "password"
    return unique_test_id, test_pw


def test_login_page_nav_link(driver):
    """Login nav-link testing."""
    driver.get("http://127.0.0.1:5000")
    nav_link = driver.find_element(by=By.ID, value="login-nav-link")
    nav_link.click()

    uid_form = driver.find_element(by=By.NAME, value="uid")
    pw_form = driver.find_element(by=By.NAME, value="pw")

    # asserting forms to enter credentials exist + are displayed
    assert uid_form.is_displayed()
    assert pw_form.is_displayed()


def test_user_register(driver, test_user):
    """User registration testing."""
    driver.get("http://127.0.0.1:5000/h/auth/sign-up")
    uid_form = driver.find_element(by=By.NAME, value="uid")
    pw_form = driver.find_element(by=By.NAME, value="pw")

    # fixture returns unique uid
    test_id, test_pw = test_user

    # registering new user
    uid_form.send_keys(test_id)
    pw_form.send_keys(test_pw)
    button = driver.find_element(by=By.ID, value="login-button")
    button.click()

    # uid display only appears when user logged in
    logged_in_indicator = driver.find_element(by=By.ID, value="uid-display")
    assert logged_in_indicator.is_displayed()


@pytest.fixture
def registered_user(driver, test_user):
    """Register user to test user login."""
    driver.get("http://127.0.0.1:5000/h/auth/sign-up")
    uid_form = driver.find_element(by=By.NAME, value="uid")
    pw_form = driver.find_element(by=By.NAME, value="pw")
    test_id, test_pw = test_user

    # registering new user
    uid_form.send_keys(test_id)
    pw_form.send_keys(test_pw)
    button = driver.find_element(by=By.ID, value="login-button")
    button.click()

    # login success check
    logged_in_indicator = driver.find_element(by=By.ID, value="uid-display")
    assert logged_in_indicator.is_displayed()

    # logging out
    button = driver.find_element(by=By.ID, value="logout-nav-link")
    button.click()
    return test_id, test_pw


def test_user_login(driver, registered_user):
    """User login testing."""
    driver.get("http://127.0.0.1:5000/h/auth/login")
    uid_form = driver.find_element(by=By.NAME, value="uid")
    pw_form = driver.find_element(by=By.NAME, value="pw")

    test_id, test_pw = registered_user  # just created

    uid_form.send_keys(test_id)
    pw_form.send_keys(test_pw)
    button = driver.find_element(by=By.ID, value="login-button")
    button.click()

    # login success check
    logged_in_indicator = driver.find_element(by=By.ID, value="uid-display")
    assert logged_in_indicator.is_displayed()
