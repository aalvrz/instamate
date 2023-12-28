import logging
import time

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

from instamate.browser import get_browser
from instamate.cookies import save_user_cookies
from instamate.exceptions import InstamateException


logger = logging.getLogger(__name__)


class AuthenticationError(InstamateException):
    """Error raised when user authentication fails."""


class AuthPage:
    """Allows logging-in using Instagram's log-in screen."""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

    def login(self) -> None:
        if self.is_user_logged_in():
            logger.info("User is already logged in. Skipping authentication.")
            return

        login_element = self._find_create_account_or_login_div()
        self._click_login_element(login_element)

        self._wait_for_login_page()

        username_input_element = self._fetch_username_input_element()
        self._enter_username(username_input_element)

        password_input_element = self._fetch_password_input_element()
        self._enter_password(password_input_element)
        time.sleep(5)

        self._press_login_button(password_input_element)
        time.sleep(5)

        self._save_login_info()

        if not self.is_user_logged_in():
            raise AuthenticationError

        save_user_cookies(self.username, get_browser().get_cookies())

    def _find_create_account_or_login_div(self):
        """
        Check if the first div is 'Create an Account' or 'Log In'

        :returns: Login element if found

        :raises: AuthenticationError if no login element is found.
        """
        try:
            login_element = get_browser().find_element(By.XPATH, "//div[text()='Log in']")
        except NoSuchElementException:
            raise AuthenticationError("Unable to locate log in element")

        return login_element

    def _click_login_element(self, login_element) -> None:
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

    def _wait_for_login_page(self, seconds=10) -> None:
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

    def _enter_username(self, username_input_element) -> None:
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

    def _enter_password(self, password_input_element) -> None:
        """Enters the provided password value in the password input element."""

        (
            ActionChains(get_browser())
            .move_to_element(password_input_element)
            .click()
            .send_keys(self.password)
            .perform()
        )

    def _press_login_button(self, password_input_element) -> None:
        (
            ActionChains(get_browser())
            .move_to_element(password_input_element)
            .click()
            .send_keys(Keys.ENTER)
            .perform()
        )

    def _save_login_info(self) -> None:
        """Clicks on the 'Save Login Info' dialog button so that Instagrams saves the auth session."""

        save_login_info_btn = get_browser().find_element(
            By.XPATH, "//button[text()='Save Info']"
        )

        if save_login_info_btn:
            ActionChains(get_browser()).move_to_element(
                save_login_info_btn
            ).click().perform()

    def is_user_logged_in(self) -> bool:
        # Use the "Your Story" element to determine if user is already logged in
        try:
            element = get_browser().find_element(By.XPATH, "//div[text()='Your story']")
            if element:
                return True
        except NoSuchElementException:
            pass

        return False
