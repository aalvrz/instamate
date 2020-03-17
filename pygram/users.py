"""Interactions with Instagram users."""
import logging
import json
import random
import time
from functools import lru_cache
from typing import List, Iterator

from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .browser import get_browser
from .constants import INSTAGRAM_HOMEPAGE_URL, FollowingStatus
from .graphql import get_graphql_query_hash
from .xpath import FOLLOW_BUTTON_XPATH


logger = logging.getLogger(__name__)


class InstagramUserOperationError(Exception):
    """
    Raised when an error occurs when doing an operation on a Instagram user.
    """


class UnfollowUserError(InstagramUserOperationError):
    """Error when trying to unfollow Instagram user."""


def user_followers(user_id: int, randomize: bool = False) -> Iterator[List[str]]:
    """
    Generator that fetches a user's followers.

    A page (represented as a list) of followers is yielded on ever iteration.
    The generator will fetch subsequent pages if there are any.
    """

    query_hash = get_graphql_query_hash()
    graphql_query_url = (
        f'view-source:https://www.instagram.com/graphql/query/?query_hash={query_hash}'
    )

    has_next_page = False

    def _get_user_followers_data(params) -> (List[str]):
        url = f'{graphql_query_url}&variables={json.dumps(params)}'
        get_browser().get(url)

        pre_element = get_browser().find_element_by_tag_name('pre')
        data = json.loads(pre_element.text)

        followers_data = data['data']['user']['edge_followed_by']
        return followers_data

    params = {'id': user_id, 'include_reel': 'true', 'fetch_mutual': 'true', 'first': 50}
    while True:
        if has_next_page:
            time.sleep(random.randint(2, 6))

        followers_data = _get_user_followers_data(params)
        followers_page = followers_data['edges']
        followers_list = [follower['node']['username'] for follower in followers_page]

        if randomize:
            random.shuffle(followers_list)

        yield followers_list

        has_next_page = followers_data['page_info']['has_next_page']

        if not has_next_page:
            break

        end_cursor = followers_data['page_info']['end_cursor']
        params['after'] = end_cursor


def user_followings(user_id: int):
    def _get_user_followings_data(params) -> (List[str]):
        url = f'{graphql_query_url}&variables={json.dumps(params)}'
        get_browser().get(url)

        pre_element = get_browser().find_element_by_tag_name('pre')
        data = json.loads(pre_element.text)

        followings_data = data['data']['user']['edge_follow']
        return followings_data

    # NOTE: It seems that the query hash for obtaining followings is different than the hash for
    # obtaining followers.
    query_hash = '58712303d941c6855d4e888c5f0cd22f'
    graphql_query_url = (
        f'view-source:https://www.instagram.com/graphql/query/?query_hash={query_hash}'
    )

    has_next_page = False

    params = {'id': user_id, 'first': 50}
    while True:
        if has_next_page:
            time.sleep(random.randint(2, 6))

        followings_data = _get_user_followings_data(params)
        followings_page = followings_data['edges']
        followings_list = [user['node']['username'] for user in followings_page]

        yield followings_list

        has_next_page = followings_data['page_info']['has_next_page']

        if not has_next_page:
            break

        end_cursor = followings_data['page_info']['end_cursor']
        params['after'] = end_cursor


class InstagramUser:
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

    def get_followers(self, randomize: bool = False) -> Iterator[str]:
        """
        Get list of followers.

        Individual usernames are yielded per iteration of this method.

        :param randomize: If list of followers should be returned in random order.
        """
        user_id = self._get_user_id()

        for page in user_followers(user_id, randomize):
            yield from page

    def get_followings(self) -> Iterator[str]:
        user_id = self._get_user_id()

        for page in user_followings(user_id):
            yield from page

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
        unfollow_button = get_browser().find_element_by_xpath("//button[text()='Unfollow']")
        unfollow_button.click()
