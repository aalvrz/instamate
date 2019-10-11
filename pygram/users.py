"""Interactions with Instagram users."""
import logging
import json
import random
import time
from functools import lru_cache
from typing import List

from selenium.common.exceptions import WebDriverException

from .browser import get_browser
from .constants import INSTAGRAM_HOMEPAGE_URL
from .graphql import get_graphql_query_hash


logger = logging.getLogger(__name__)


class InstagramUserOperationError(Exception):
    """
    Raised when an error occurs when doing an operation on a Instagram user.
    """


def user_followers(user_id: int) -> List[str]:
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
        yield followers_page

        has_next_page = followers_data['page_info']['has_next_page']

        if not has_next_page:
            break

        end_cursor = followers_data['page_info']['end_cursor']
        params['after'] = end_cursor


class InstagramUser:
    def __init__(self, username: str):
        self.username = username.strip().lower()
        self.user_profile_link = f'{INSTAGRAM_HOMEPAGE_URL}/{self.username}/'

    @lru_cache(maxsize=128)
    def get_followers_count(self) -> int:
        """Returns the number of followers of this user."""

        try:
            followers_count = get_browser().execute_script(
                'return window._sharedData.entry_data.'
                'ProfilePage[0].graphql.user.edge_followed_by.count'
            )
        except WebDriverException:
            raise InstagramUserOperationError("Failed to get {self.username}'s follower count.")

        return int(followers_count)

    def get_followers(self, randomize=False) -> List[str]:
        """
        Get list of followers.

        :param randomize: If list of followers should be returned in random order.
        """
        followers = []
        user_id = self._get_user_id()

        for page in user_followers(user_id):
            for follower in page:
                followers.append(follower['node']['username'])

        if randomize:
            random.shuffle(followers)

        return followers

    @lru_cache(maxsize=128)
    def get_followings_count(self) -> int:
        """Returns the number of followings of this user."""

        try:
            following_count = get_browser().execute_script(
                'return window._sharedData.entry_data.'
                'ProfilePage[0].graphql.user.edge_follow.count'
            )
        except WebDriverException:
            raise InstagramUserOperationError("Failed to get {self.username}'s following count.")

        return int(following_count)

    @lru_cache(maxsize=128)
    def _get_user_id(self) -> int:
        get_browser().get(self.user_profile_link)

        try:
            user_id = get_browser().execute_script(
                'return window.__additionalData[Object.keys(window.__additionalData)[0]].data.graphql.user.id'
            )
        except WebDriverException:
            user_id = get_browser().execute_script(
                'return window._sharedData.' 'entry_data.ProfilePage[0].' 'graphql.user.id'
            )

        return str(user_id)
