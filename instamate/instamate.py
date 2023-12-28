import datetime
import logging
from typing import Dict, Iterable

import httpx

from .cookies import load_user_cookies
from .pages.auth import AuthPage
from .browser import get_browser
from .constants import INSTAGRAM_HOMEPAGE_URL
from .following import follow_users
from .logging import INSTAMATE_LOG_FORMATTER, InstamateLoggerContextFilter
from instamate.queries.graphql import GraphQLAPI
from instamate.queries.user import GetUserDataQuery


logger = logging.getLogger("instamate")


class Instamate:
    """Initializes an Instamate session with a browser.

    Browser will be closed when the session finishes.
    """

    def __init__(self, username: str, password: str) -> None:
        """
        Args:
            username (str): Instagram username of the user to authenticate as.
            password (str): Instagram password of the user to authenticate as.
        """
        self.username = username
        self.password = password

        self._setup_logger()

        self.browser = get_browser()

        self.user_ids_cache: Dict[str, str] = {}

    def __enter__(self):
        logger.info("Initializing new Instamate session for user '%s'" % self.username)

        self.browser.implicitly_wait(5)
        self.browser.get(INSTAGRAM_HOMEPAGE_URL)

        self._load_cookies()

        self._login()

        self._init_http_client()

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

    def _setup_logger(self) -> None:
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setFormatter(INSTAMATE_LOG_FORMATTER)

        # Filters attached to the parent logger DO NOT propagate to child loggers, this is why we
        # attach the filter to the handler instead.
        handler.addFilter(InstamateLoggerContextFilter(self.username))
        logger.addHandler(handler)

    def _load_cookies(self) -> None:
        """Attempts to load any local saved cookies for the current session user."""

        cookies = load_user_cookies(self.username)
        for cookie in cookies:
            self.browser.add_cookie(cookie)

        self.browser.refresh()

    def _login(self):
        """Login the user using the crendetials provided."""

        authenticator = AuthPage(self.username, self.password)
        authenticator.login()

    def get_instagram_user_id(self, username: str) -> str | None:
        """Returns the Instagram PK user ID.

        Args:
            username (str): Instagram username handle without `@` prefix.

        Returns:
            str: String of the unique user ID.
        """
        user_id = self.user_ids_cache.get(username)
        if user_id:
            return user_id

        user_data = GetUserDataQuery().get_user_data(username)
        user_id = user_data.get("pk")

        if user_id:
            logger.info("Caching user ID '%s' for user '%s'" % (user_id, username))
            self.user_ids_cache[username] = user_id

        return user_id

    def get_user_followers(self, username: str) -> Iterable[str]:
        logger.info("Fetching all followers for user '%s'" % username)

        user_id = self.get_instagram_user_id(username)

        if not user_id:
            logger.error("Could not get user_id from query")
            return []

        followers = GraphQLAPI(self.http_client).get_followers(user_id)
        return followers

    def get_user_followings(self, username: str) -> Iterable[str]:
        logger.info("Fetching all followings for user '%s'" % username)

        user_id = self.get_instagram_user_id(username)

        if not user_id:
            logger.error("Could not get user_id from query")
            return []

        followings = GraphQLAPI(self.http_client).get_followings(user_id)
        return followings

    def follow_user_followers(
        self,
        username: str,
        amount: int = 100,
        # parameters: Optional[FollowParameters] = None,
    ) -> None:
        """Follows all the followers of a specific user."""

        logger.info("Preparing to follow %d followers of user @%s" % (amount, username))

        users = self.get_user_followers(username)
        follow_users(users, amount)

    def unfollow_users(self, until_datetime: datetime.datetime | None = None) -> None:
        """
        Unfollow users that this account is following.

        For now only unfollow users that have been followed through Instamate, and that DON'T
        follow back this account.

        :param until_datetime: Only unfollow users that were followed at this datetime and
                               before. Users followed after this time will not be unfollowed.
        """
        raise NotImplementedError
