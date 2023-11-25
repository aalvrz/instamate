"""
Pygram - The Python bot for Instagram


Commands:

    - `follow_user_followers: Obtains the list of followers of a specific user
                              and follows them.
"""
import datetime
import logging
from typing import Iterable, Optional

import httpx

from .auth import AuthPage
from .browser import get_browser
from .constants import INSTAGRAM_HOMEPAGE_URL
from .following import FollowHandler, FollowParameters
from .logging import PYGRAM_LOG_FORMATTER, PygramLoggerContextFilter
from .unfollowing import UnfollowHandler
from .pages.profile import UserProfilePage
from .workspace import UserWorkspace
from pygram.queries.graphql import GraphQLAPI
from pygram.queries.user import GetUserDataQuery


logger = logging.getLogger("pygram")


class Pygram:
    """Initializes a Pygram session."""

    def __init__(self, username: str, password: str):
        """
        Args:
            username (str): Instagram username of the user to authenticate as.
            password (str): Instagram password of the user to authenticate as.
        """
        self.username = username
        self.password = password

        self._setup_logger()

        self.browser = get_browser()
        self.workspace = UserWorkspace(self.username)

    def __enter__(self):
        self.browser.implicitly_wait(5)
        self._login()

        self.http_client = httpx.Client()

        return self

    def __exit__(self, type, exc_value, traceback):
        self.browser.quit()
        self.http_client.close()

    def _init_http_client(self) -> None:
        """Initializes an HTTP client with the cookies loaded for the web browser."""

        cookies = {
            cookie_dict["name"]: cookie_dict["value"]
            for cookie_dict in self.browser.get_cookies()
        }

        self.http_client = httpx.Client(cookies=cookies)

    def _setup_logger(self):
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setFormatter(PYGRAM_LOG_FORMATTER)

        # Filters attached to the parent logger DO NOT propagate to child loggers, this is why we
        # attach the filter to the handler instead.
        handler.addFilter(PygramLoggerContextFilter(self.username))
        logger.addHandler(handler)

    def _login(self):
        """Login the user using the crendetials provided."""

        get_browser().get(INSTAGRAM_HOMEPAGE_URL)

        authenticator = AuthPage(self.username, self.password)
        authenticator.login()

        logger.info("Logged in successfully.")

    def get_user_followers(self, username: str) -> Iterable[str]:
        logger.info("Fetching all followers for user '%s'" % username)

        users_data = GetUserDataQuery().get_user_data(username)
        user_id = users_data.get("pk")

        if not user_id:
            logger.error("Could not get user_id from query")
            return []

        followers = GraphQLAPI(self.http_client).get_followers(user_id)
        return followers

    def get_user_followings(self, username: str) -> Iterable[str]:
        logger.info("Fetching all followings for user '%s'" % username)

        users_data = GetUserDataQuery().get_user_data(username)
        user_id = users_data.get("pk")

        if not user_id:
            logger.error("Could not get user_id from query")
            return []

        followings = GraphQLAPI(self.http_client).get_followings(user_id)
        return followings

    def follow_user_followers(
        self, username: str, amount: int = 100, parameters: FollowParameters = None
    ):
        """
        Obtains the list of followers of a specific user and follows them.
        """

        logger.info(f"Obtaining {username}'s followers.")

        user = UserProfilePage(username)
        user_followers = user.get_followers(randomize=True)

        handler = FollowHandler(user=self.username, parameters=parameters)
        self.follows_count = handler.follow_users(
            users_to_follow=user_followers, amount=amount
        )

        logger.info(f"Finished following {amount} of {username}'s followers")

    def unfollow_users(self, until_datetime: Optional[datetime.datetime] = None):
        """
        Unfollow users that this account is following.

        For now only unfollow users that have been followed through Pygram, and that DON'T
        follow back this account.

        :param until_datetime: Only unfollow users that were followed at this datetime and
                               before. Users followed after this time will not be unfollowed.
        """

        logger.info("Starting to unfollow users...")

        handler = UnfollowHandler(self.username, until_datetime)
        self.unfollows_count = handler.unfollow_users()

        logger.info(f"Unfollowed a total of {self.unfollows_count} users")
