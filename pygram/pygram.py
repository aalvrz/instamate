"""
Pygram - The Python bot for Instagram


Commands:

    - `follow_user_followers: Obtains the list of followers of a specific user
                              and follows them.
"""
import datetime
import logging
from typing import Dict

from .auth import Authenticator
from .browser import get_browser
from .constants import INSTAGRAM_HOMEPAGE_URL
from .db import get_database
from .following import FollowHandler, FollowParameters
from .logging import PYGRAM_LOG_FORMATTER, PygramLoggerContextFilter
from .unfollowing import UnfollowHandler
from .sms import SMSClient
from .users import InstagramUser
from .workspace import UserWorkspace


logger = logging.getLogger('pygram')
database = get_database()


class Pygram:
    """
    Initializes a Pygram session.

    To enable SMS notifications, provide a `sms_config` dictionary argument:

    {
        'sid': 'Aaksdlkasdk',
        'token': 'Xdkgouasd9f912',
        'from_number': '+19732644152',
        'to_number': '+1230349349',
    }
    """

    def __init__(self, username: str, password: str, sms_config: Dict = None):
        self.username = username
        self.password = password
        self._sms_client = None

        if sms_config:
            self._sms_client = SMSClient(**sms_config)

        self._setup_logger()

        self.workspace = UserWorkspace(self.username)

        database.create_profile(self.username)

        self.follows_count = 0
        self.unfollows_count = 0

    def __enter__(self):
        get_browser().implicitly_wait(5)

        self._login()

        self._record_account_progress()

        return self

    def __exit__(self, type, value, traceback):
        get_browser().quit()
        database.close()

        if not value:
            self._record_session_activity()

    def _setup_logger(self):
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setFormatter(PYGRAM_LOG_FORMATTER)

        # Filters attached to the parent logger DO NOT propagate to child loggers, this is why we
        # attach the filter to the handler instead.
        handler.addFilter(PygramLoggerContextFilter(self.username))
        logger.addHandler(handler)

    def _login(self):
        """
        Login the user using the crendetials provided.
        """

        get_browser().navigate(INSTAGRAM_HOMEPAGE_URL)

        authenticator = Authenticator(self.username, self.password)
        authenticator.login()

        logger.info('Logged in successfully.')

    def _record_account_progress(self):
        logger.info('Saving account progress...')

        user = InstagramUser(self.username)
        posts_count, followers_count, following_count = user.get_all_activity_counts()
        logger.info('Posts: %d | Followers: %d | Following: %d' % (posts_count, followers_count, following_count))

        database.record_account_progress(
            username=self.username,
            followers_count=followers_count,
            following_count=following_count,
            total_posts_count=posts_count,
        )

    def _record_session_activity(self):
        database.record_activity(
            username=self.username,
            follows_count=self.follows_count,
            unfollows_count=self.unfollows_count,
        )

        if self._sms_client:
            self._sms_client.send_session_report_sms(follows_count=self.follows_count)

    def get_user_followers(self, username: str) -> int:
        user = InstagramUser(username)
        return user.get_followers()

    def follow_user_followers(
        self, username: str, amount: int = 100, parameters: FollowParameters = None
    ):
        """
        Obtains the list of followers of a specific user and follows them.
        """

        logger.info(f"Obtaining {username}'s followers.")

        user = InstagramUser(username)
        user_followers = user.get_followers(randomize=True)

        handler = FollowHandler(user=self.username, parameters=parameters)
        self.follows_count = handler.follow_users(users_to_follow=user_followers, amount=amount)

        logger.info(f"Finished following {amount} of {username}'s followers")

    def unfollow_users(self, until_datetime: datetime.datetime = None):
        """
        Unfollow users that this account is following.

        For now only unfollow users that have been followed through Pygram, and that DON'T
        follow back this account.

        :param until_datetime: Only unfollow users that were followed at this datetime and
                               before. Users followed after this time will not be unfollowed.
        """

        logger.info('Starting to unfollow users...')

        handler = UnfollowHandler(self.username, until_datetime)
        self.unfollows_count = handler.unfollow_users()

        logger.info(f'Unfollowed a total of {self.unfollows_count} users')
