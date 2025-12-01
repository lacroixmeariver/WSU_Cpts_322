"""Tests for page navigation."""

import pytest
from selenium import webdriver


@pytest.fixture
def driver():
    """Establish driver for testing use."""
    driver = webdriver.Firefox()  # opens firefox browser window
    yield driver  # hand driver over to the test
    driver.quit()


def test_index_page_loads(driver):
    """Testing that index page loads."""
    driver.get("http://127.0.0.1:5000")
    assert driver.title == "HOMEPAGE"
    assert "error" not in driver.page_source.lower()


def test_admin_page_loads(driver):
    """Testing that  page loads."""
    driver.get("http://127.0.0.1:5000/h/admin/dashboard")
    assert driver.title == "DASHBOARD"
    assert "error" not in driver.page_source.lower()


def test_analytics_page_loads(driver):
    """Testing that  page loads."""
    driver.get("http://127.0.0.1:5000/h/analytics/home")
    assert driver.title == "ANALYTICS"
    assert "error" not in driver.page_source.lower()


def test_add_club_page_loads(driver):
    """Testing that  page loads."""
    driver.get("http://127.0.0.1:5000/h/admin/add-club")
    assert driver.title != ""
    assert "error" not in driver.page_source.lower()


def test_assign_room_page_loads(driver):
    """Testing that  page loads."""
    driver.get("http://127.0.0.1:5000/h/admin/assign-room-to-club")
    assert driver.title != ""
    assert "error" not in driver.page_source.lower()


def test_view_club_page_loads(driver):
    """Testing that  page loads."""
    driver.get("http://127.0.0.1:5000/admin/clubs")
    assert driver.title != ""
    assert "error" not in driver.page_source.lower()
