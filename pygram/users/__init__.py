"""Interactions with Instagram users."""
import logging
import time
from functools import lru_cache
from typing import Iterator, Tuple

from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..browser import get_browser
from ..constants import INSTAGRAM_HOMEPAGE_URL, FollowingStatus
from ..xpath import FOLLOW_BUTTON_XPATH
from .followers import UserFollowers
from .followings import UserFollowings


logger = logging.getLogger(__name__)


class InstagramUserOperationError(Exception):
    """
    Raised when an error occurs when doing an operation on a Instagram user.
    """


class UnfollowUserError(InstagramUserOperationError):
    """Error when trying to unfollow Instagram user."""


class InstagramUser:

    # Base query for obtaining certain user data
    base_query = 'return window.__additionalData[Object.keys(window.__additionalData)[0]].data.'

    def __init__(self, username: str):
        self.username = username.strip().lower()
        self.user_profile_link = f'{INSTAGRAM_HOMEPAGE_URL}/{self.username}/'

    def __str__(self):
        return self.username

    def get_following_status(self, current_username: str) -> FollowingStatus:
        """
        Return the following status for this user.

        :param current_username: Username of the current session's user.

        :returns: A FollowingStatus enum value representing the following status.
        """

        if self.username == current_username:
            raise InstagramUserOperationError("Can't get following status of same user")

        get_browser().navigate(self.user_profile_link)

        try:
            follow_button_elem = WebDriverWait(get_browser(), 10).until(
                EC.presence_of_element_located((By.XPATH, FOLLOW_BUTTON_XPATH))
            )
        except TimeoutException:
            raise

        following_status = follow_button_elem.text

        return FollowingStatus.get_following_status_from_string(following_status)

    @property
    def is_private(self):
        """Check if this user has a private profile."""

        is_private = None
        try:
            is_private = get_browser().execute_script(
                'return window.__additionalData[Object.keys(window.__additionalData)[0]].'
                'data.graphql.user.is_private'
            )
        except WebDriverException:
            try:
                get_browser().execute_script('location.reload()')

                is_private = get_browser().execute_script(
                    'return window._sharedData.entry_data.' 'ProfilePage[0].graphql.user.is_private'
                )
            except WebDriverException:
                pass

        return is_private

    @property
    def is_business_account(self) -> bool:
        is_business_account = False

        get_browser().navigate(self.user_profile_link)

        query = 'graphql.user.is_business_account'
        try:
            is_business_account = get_browser().execute_script(self.base_query + query)
        except WebDriverException:
            try:
                get_browser().execute_script('location.reload()')

                is_business_account = get_browser().execute_script(
                    'return window._sharedData.entry_data.ProfilePage[0].' + query
                )
            except WebDriverException as ex:
                logging.error(f'Error determining if {self.username} is a business account: {ex}')

        return is_business_account

    @lru_cache(maxsize=128)
    def get_followers_count(self) -> int:
        """Navigates to the user's profile and returns the number of followers of this user."""

        get_browser().navigate(self.user_profile_link)

        try:
            followers_count = get_browser().execute_script(
                'return window._sharedData.entry_data.'
                'ProfilePage[0].graphql.user.edge_followed_by.count'
            )
        except WebDriverException:
            raise InstagramUserOperationError("Failed to get {self.username}'s follower count.")

        return int(followers_count)

    def get_followers(self, randomize: bool = True) -> Iterator[str]:
        """
        Get list of followers.

        Individual usernames are yielded per iteration of this method.

        :param randomize: If list of followers should be returned in random order.
        """
        user_id = self._get_user_id()
        return UserFollowers(user_id, randomize)

    def get_followings(self) -> Iterator[str]:
        user_id = self._get_user_id()
        return UserFollowings(user_id, randomize=False)

    def get_all_activity_counts(self) -> Tuple[int, int, int]:
        """
        Returns 3 item tuple containing counts for this user's total posts, followers, and
        followings.
        """

        get_browser().navigate(self.user_profile_link)
        time.sleep(3)

        followings_count = self.get_followings_count()
        total_posts_count = self.get_total_posts_count()
        followers_count = self.get_followers_count()

        return (total_posts_count, followers_count, followings_count)

    @lru_cache(maxsize=128)
    def get_followings_count(self) -> int:
        """Navigates to the user's profile and returns the number of followings of this user."""

        get_browser().navigate(self.user_profile_link)

        try:
            following_count = get_browser().execute_script(
                'return window._sharedData.entry_data.'
                'ProfilePage[0].graphql.user.edge_follow.count'
            )
        except WebDriverException:
            raise InstagramUserOperationError("Failed to get {self.username}'s following count.")

        return int(following_count)

    def get_total_posts_count(self) -> int:
        """Navigates to the user's profile and returns the number of posts of this user."""

        data = None
        query = 'graphql.user.edge_owner_to_timeline_media.count'

        get_browser().navigate(self.user_profile_link)

        try:
            base_query = (
                'return window.__additionalData[Object.keys(window.__additionalData)[0]].data.'
            )
            data = get_browser().execute_script(base_query + query)
        except WebDriverException:
            get_browser().execute_script('location.reload()')

            base_query = 'return window._sharedData.entry_data.ProfilePage[0].'
            data = get_browser().execute_script(base_query + query)

        return data

    @lru_cache(maxsize=128)
    def _get_user_id(self) -> int:
        get_browser().navigate(self.user_profile_link)

        try:
            user_id = get_browser().execute_script(
                'return window.__additionalData[Object.keys(window.__additionalData)[0]].data.graphql.user.id'
            )
        except WebDriverException:
            user_id = get_browser().execute_script(
                'return window._sharedData.' 'entry_data.ProfilePage[0].' 'graphql.user.id'
            )

        return str(user_id)

    def follow(self):
        """Follows this user from their profile page."""

        get_browser().navigate(self.user_profile_link)
        time.sleep(5)

        follow_button_xp = get_browser().find_element_by_xpath(FOLLOW_BUTTON_XPATH)

        try:
            follow_button_xp.click()
        except:
            logger.error(f'Error trying to follow user {self}')

    def unfollow(self):
        """
        Navigate to this user's profile and unfollow.

        :raises UnfollowUserError: If user can't be unfollowed.
        """

        get_browser().navigate(self.user_profile_link)
        time.sleep(5)

        try:
            button = get_browser().find_element_by_xpath("//button[text() = 'Following']")
        except NoSuchElementException:
            try:
                button = get_browser().find_element_by_xpath(
                    "//button/div/span[contains(@aria-label, 'Following')]"
                )
            except NoSuchElementException:
                raise UnfollowUserError('Cannot locate unfollow button')

        button.click()

        # Confirm unfollow
        time.sleep(2)

        unfollow_button = get_browser().find_element_by_xpath("//button[text()='Unfollow']")
        unfollow_button.click()
