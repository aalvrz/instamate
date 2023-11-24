import logging
import time

from selenium.common.exceptions import (
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .browser import get_browser
from .exceptions import PygramException
from .workspace import UserWorkspace, CookiesFileNotFoundError


logger = logging.getLogger(__name__)


class AuthenticationError(PygramException):
    """Error raised when user authentication fails."""


class Authenticator:
    """
    Logs into Instagram

    The authenticator is responsible for waiting and locating the elements in
    the DOM that allow entering the credentials provided for logging in.
    """

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        self._user_workspace = UserWorkspace(self.username)
        self._cookie_loaded = False

    def login(self):
        try:
            self._login_using_cookie()
        except CookiesFileNotFoundError:
            logger.warning("Could not login using auth cookie")

        if self.is_user_logged_in():
            return

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
        time.sleep(5)

        # TODO: Handle "Save Your Login Info" dialog

        if not self.is_user_logged_in():
            raise AuthenticationError

        self._store_user_cookies()

    def _login_using_cookie(self):
        # We will first try to log the user in using a cookie. If the login is
        # successful, the user should show as logged in after refreshing the
        # page.
        self._load_user_cookies()
        get_browser().refresh()
        time.sleep(2)

    def _find_create_account_or_login_div(self):
        """
        Check if the first div is 'Create an Account' or 'Log In'

        :returns: Login element if found

        :raises: AuthenticationError if no login element is found.
        """
        try:
            login_element = get_browser().find_element(
                By.XPATH, "//div[text()='Log in']"
            )
        except NoSuchElementException:
            raise AuthenticationError("Unable to locate log in element")

        return login_element

    def _click_login_element(self, login_element):
        """Clicks login element so that login is possible."""

        if login_element is not None:
            try:
                (
                    ActionChains(get_browser())
                    .move_to_element(login_element)
                    .click()
                    .perform()
                )
            except MoveTargetOutOfBoundsException:
                login_element.click()

    def _wait_for_login_page(self, seconds=10):
        try:
            WebDriverWait(get_browser(), seconds).until(EC.title_contains("Instagram"))
        except TimeoutException:
            raise AuthenticationError("Could not find login page")

    def _fetch_username_input_element(self, seconds: int = 10):
        """
        Wait until the 'username' input element is located and visible.

        :param seconds: Seconds to wait for element.

        :returns: Username input element if found.

        :raises: AuthenticationError if username input element is not found.
        """
        try:
            username_element = WebDriverWait(get_browser(), seconds).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
            )
        except TimeoutException:
            raise AuthenticationError("Could not find username input element")

        return username_element

    def _enter_username(self, username_input_element):
        """Enters the provided username value in the input element."""
        (
            ActionChains(get_browser())
            .move_to_element(username_input_element)
            .click()
            .send_keys(self.username)
            .perform()
        )

    def _fetch_password_input_element(self):
        password_element = get_browser().find_element(
            By.XPATH, "//input[@name='password']"
        )
        return password_element

    def _enter_password(self, password_input_element):
        """Enters the provided password value in the password input element."""

        (
            ActionChains(get_browser())
            .move_to_element(password_input_element)
            .click()
            .send_keys(self.password)
            .perform()
        )

    def _press_login_button(self, password_input_element):
        (
            ActionChains(get_browser())
            .move_to_element(password_input_element)
            .click()
            .send_keys(Keys.ENTER)
            .perform()
        )

    def _load_user_cookies(self):
        """
        Load a user cookies that already contain session data.
        """

        for cookie in self._user_workspace.get_cookies():
            get_browser().add_cookie(cookie)

        self._cookie_loaded = True

    def _store_user_cookies(self):
        """
        Create session cookies for user and store it in the user's workspace.
        """
        self._user_workspace.store_cookies(get_browser().get_cookies())

    def is_user_logged_in(self) -> bool:
        # Check using activity counts
        # If user is not logged in, JavaScript will return null for activity
        # counts.
        try:
            activity_counts = get_browser().execute_script(
                "return window._sharedData.activity_counts"
            )
        except WebDriverException:
            try:
                get_browser().excecute_script("location.reload()")
                # TODO: Update activity
                activity_counts = get_browser().execute_script(
                    "return window._sharedData.activity_counts"
                )
            except WebDriverException:
                activity_counts = None

        try:
            activity_counts_new = get_browser().execute_script(
                "return window._sharedData.config.viewer"
            )
        except WebDriverException:
            try:
                get_browser().refresh()
                activity_counts_new = get_browser().execute_script(
                    "return window._sharedData.config.viewer"
                )
            except WebDriverException:
                activity_counts_new = None

        if activity_counts is None and activity_counts_new is None:
            return False

        return True
