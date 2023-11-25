"""Interactions with Instagram users."""
import logging
import time
from functools import lru_cache
from typing import Optional, Tuple

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..browser import get_browser
from ..constants import INSTAGRAM_HOMEPAGE_URL, FollowingStatus
from ..xpath import FOLLOW_BUTTON_XPATH
from .base import BaseInstagramPage


logger = logging.getLogger("pygram." + __name__)


class InstagramUserOperationError(Exception):
    """
    Raised when an error occurs when doing an operation on a Instagram user.
    """


class UnfollowUserError(InstagramUserOperationError):
    """Error when trying to unfollow Instagram user."""


class UserProfilePage(BaseInstagramPage):
    """Represents the profile screen of a specific Instagram user."""

    # Base query for obtaining certain user data
    base_query = (
        "return window.__additionalData[Object.keys(window.__additionalData)[0]].data."
    )

    def __init__(self, username: str):
        """Initialize a new user profile page for a specific user.

        Args:
            username (str): Instagram username without `@` prefix.
        """
        super().__init__()

        self.username = username.strip().lower()
        self.link = f"{INSTAGRAM_HOMEPAGE_URL}/{self.username}/"

    def get_following_status(self) -> FollowingStatus:
        """Return the following status between this profile's user and the current session's user.

        :returns: A FollowingStatus enum value representing the following status.
        """
        try:
            follow_button_elem = WebDriverWait(get_browser(), 10).until(
                EC.presence_of_element_located((By.XPATH, FOLLOW_BUTTON_XPATH))
            )
        except TimeoutException:
            raise

        status_txt = follow_button_elem.text
        following_status = FollowingStatus(status_txt)
        return following_status

    @property
    def is_private(self):
        """Check if this user has a private profile."""

        is_private = None
        try:
            is_private = get_browser().execute_script(
                "return window.__additionalData[Object.keys(window.__additionalData)[0]]."
                "data.graphql.user.is_private"
            )
        except WebDriverException:
            try:
                get_browser().execute_script("location.reload()")

                is_private = get_browser().execute_script(
                    "return window._sharedData.entry_data."
                    "ProfilePage[0].graphql.user.is_private"
                )
            except WebDriverException:
                pass

        return is_private

    @property
    def is_business_account(self) -> bool:
        is_business_account = False

        get_browser().get(self.link)

        query = "graphql.user.is_business_account"
        try:
            is_business_account = get_browser().execute_script(self.base_query + query)
        except WebDriverException:
            try:
                get_browser().execute_script("location.reload()")

                is_business_account = get_browser().execute_script(
                    "return window._sharedData.entry_data.ProfilePage[0]." + query
                )
            except WebDriverException as ex:
                logging.error(
                    f"Error determining if {self.username} is a business account: {ex}"
                )

        return is_business_account

    @lru_cache(maxsize=128)
    def get_followers_count(self) -> Optional[int]:
        """Navigates to the user's profile and returns the number of followers of this user."""

        followers_count: Optional[int] = None

        try:
            followers_count = get_browser().execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.edge_followed_by.count"
            )
        except WebDriverException as ex:
            logger.warning(
                "Could not get %s's followers count: %s" % (self.username, ex)
            )

        return followers_count

    def get_all_activity_counts(
        self
    ) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Returns 3 item tuple containing counts for this user's total posts, followers, and
        followings.
        """
        followings_count = self.get_followings_count()
        time.sleep(3)

        total_posts_count = self.get_total_posts_count()
        time.sleep(3)

        followers_count = self.get_followers_count()
        time.sleep(3)

        return (total_posts_count, followers_count, followings_count)

    @lru_cache(maxsize=128)
    def get_followings_count(self) -> Optional[int]:
        """Navigates to the user's profile and returns the number of followings of this user."""

        following_count: Optional[int] = None

        try:
            following_count = get_browser().execute_script(
                "return window._sharedData.entry_data."
                "ProfilePage[0].graphql.user.edge_follow.count"
            )

            if following_count:
                following_count = int(following_count)
        except (WebDriverException, TypeError) as ex:
            logger.warning(
                "Could not obtain %s's followings count: %s" % (self.username, ex)
            )

        return following_count

    def get_total_posts_count(self) -> Optional[int]:
        """Navigates to the user's profile and returns the number of posts of this user."""

        posts_count: Optional[int] = None
        query = "graphql.user.edge_owner_to_timeline_media.count"

        try:
            base_query = "return window.__additionalData[Object.keys(window.__additionalData)[0]].data."
            posts_count = self.browser.execute_script(base_query + query)
        except WebDriverException as ex:
            logger.warning(
                "Could not get %s's total posts count: %s" % (self.username, ex)
            )

        return posts_count

    @lru_cache(maxsize=128)
    def _get_user_id(self) -> str:
        """Attemps to obtain the user ID of the current profile page."""

        try:
            user_id = self.browser.execute_script(
                "return window.__additionalData[Object.keys(window.__additionalData)[0]].data.graphql.user.id"
            )
        except WebDriverException:
            user_id = self.browser.execute_script(
                "return window._sharedData.entry_data.ProfilePage[0].graphql.user.id"
            )

        return str(user_id)

    def follow(self) -> None:
        """Follows this user from their profile page."""

        follow_button_xp = self.browser.find_element(By.XPATH, FOLLOW_BUTTON_XPATH)

        try:
            follow_button_xp.click()
        except WebDriverException as ex:
            logger.error("Error trying to follow user '%s': %s" % (self.username, ex))
        else:
            logger.info("Followed user '%s'" % self.username)

    def unfollow(self):
        """
        Navigate to this user's profile and unfollow.

        :raises UnfollowUserError: If user can't be unfollowed.
        """

        get_browser().get(self.link)
        time.sleep(5)

        try:
            button = get_browser().find_element_by_xpath(
                "//button[text() = 'Following']"
            )
        except NoSuchElementException:
            try:
                button = get_browser().find_element_by_xpath(
                    "//button/div/span[contains(@aria-label, 'Following')]"
                )
            except NoSuchElementException:
                raise UnfollowUserError("Cannot locate unfollow button")

        button.click()

        # Confirm unfollow
        time.sleep(2)

        unfollow_button = get_browser().find_element_by_xpath(
            "//button[text()='Unfollow']"
        )
        unfollow_button.click()

    def __str__(self) -> str:
        return self.username
