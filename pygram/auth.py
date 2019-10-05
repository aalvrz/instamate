import time
from functools import lru_cache

from selenium.common.exceptions import (
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .exceptions import PygramException
from .workspace import UserWorkspace


class AuthenticationError(PygramException):
    """Error raised when user authentication fails."""


class Authenticator:
    """
    Logs into Instagram

    The authenticator is responsible for waiting and locating the elements in
    the DOM that allow entering the credentials provided for logging in.
    """

    def __init__(self, username: str, password: str, browser):
        self.username = username
        self.password = password
        self.browser = browser

        self._user_workspace = UserWorkspace(self.username)
        self._cookie_loaded = False

    def login(self):
        login_element = self._find_create_account_or_login_div()
        self._click_login_element(login_element)

        # TODO: Record activity

        self._wait_for_login_page()

        username_input_element = self._fetch_username_input_element()
        self._enter_username(username_input_element)

        password_input_element = self._fetch_password_input_element()
        self._enter_password(password_input_element)

        time.sleep(1)

        self._press_login_button(password_input_element)

    def _find_create_account_or_login_div(self):
        """
        Check if the first div is 'Create an Account' or 'Log In'

        :returns: Login element if found

        :raises: AuthenticationError if no login element is found.
        """
        try:
            login_element = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[text()='Log In']"))
            )
        except TimeoutException:
            try:
                login_element = self.browser.find_element_by_xpath("//a[text()='Log in']")
            except NoSuchElementException:
                raise AuthenticationError('Unable to locate log in element')

        return login_element

    def _click_login_element(self, login_element):
        """Clicks login element so that login is possible."""

        if login_element is not None:
            try:
                (ActionChains(self.browser).move_to_element(login_element).click().perform())
            except MoveTargetOutOfBoundsException:
                login_element.click()

    def _wait_for_login_page(self, seconds=10):
        try:
            WebDriverWait(self.browser, seconds).until(EC.title_contains('Login'))
        except TimeoutException:
            raise AuthenticationError('Could not find login page')

    def _fetch_username_input_element(self, seconds: int = 10):
        """
        Wait until the 'username' input element is located and visible.

        :param seconds: Seconds to wait for element.

        :returns: Username input element if found.

        :raises: AuthenticationError if username input element is not found.
        """
        try:
            username_element = WebDriverWait(self.browser, seconds).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
            )
        except TimeoutException:
            raise AuthenticationError('Could not find username input element')

        return username_element

    def _enter_username(self, username_input_element):
        """Enters the provided username value in the input element."""
        (
            ActionChains(self.browser)
            .move_to_element(username_input_element)
            .click()
            .send_keys(self.username)
            .perform()
        )

    def _fetch_password_input_element(self):
        password_element = self.browser.find_elements_by_xpath("//input[@name='password']")

        return password_element

    def _enter_password(self, password_input_element):
        """Enters the provided password value in the input element."""
        (
            ActionChains(self.browser)
            .move_to_element(password_input_element[0])
            .click()
            .send_keys(self.password)
            .perform()
        )

    def _press_login_button(self, password_input_element):
        (
            ActionChains(self.browser)
            .move_to_element(password_input_element[0])
            .click()
            .send_keys(Keys.ENTER)
            .perform()
        )

    def _store_user_cookies(self):
        """
        Create session cookies for user and store it in the user's workspace.
        """
        if self.is_logged_in:
            self._user_workspace.store_cookies(self.browser.get_cookies())

    @property
    @lru_cache(maxsize=128)
    def is_logged_in(self):
        # User is logged in if there are two nav elements
        navs = self.browser.find_elements_by_xpath('//nav')
        return len(navs) == 2
