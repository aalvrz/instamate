"""Interactions with Instagram users."""
import logging
from functools import lru_cache

from selenium.common.exceptions import WebDriverException

from .constants import INSTAGRAM_HOMEPAGE_URL


logger = logging.getLogger(__name__)


class InstagramUserOperationError(Exception):
    """
    Raised when an error occurs when doing an operation on a Instagram user.
    """


class InstagramUser:
    def __init__(self, username: str, browser):
        self.username = username.strip().lower()
        self.user_profile_link = f'{INSTAGRAM_HOMEPAGE_URL}/{self.username}/'

        self._browser = browser

    @lru_cache(maxsize=128)
    def get_followers_count(self) -> int:
        """Returns the number of followers of this user."""

        try:
            followers_count = self.browser.execute_script(
                'return window._sharedData.entry_data.'
                'ProfilePage[0].graphql.user.edge_followed_by.count'
            )
        except WebDriverException:
            raise InstagramUserOperationError("Failed to get {self.username}'s follower count.")

        return int(followers_count)

    @lru_cache(maxsize=128)
    def get_followings_count(self) -> int:
        """Returns the number of followings of this user."""

        try:
            following_count = browser.execute_script(
                'return window._sharedData.entry_data.'
                'ProfilePage[0].graphql.user.edge_follow.count'
            )
        except WebDriverException:
            raise InstagramUserOperationError("Failed to get {self.username}'s following count.")

        return int(following_count)
