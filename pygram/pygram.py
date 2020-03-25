"""
Pygram - The Python bot for Instagram


Commands:

    - `follow_user_followers: Obtains the list of followers of a specific user
                              and follows them.
"""
import datetime
import logging
import sys
import time
from typing import Dict

from .auth import Authenticator
from .browser import get_browser
from .constants import INSTAGRAM_HOMEPAGE_URL
from .db import get_database
from .following import (
    FOLLOW_BREAK_WAIT_TIME,
    FOLLOW_COUNT_PAUSE_THRESHOLD,
    FOLLOW_USER_WAIT_TIME,
    FollowHandler,
    FollowParameters,
)
from .sms import SMSClient
from .users import InstagramUser, UnfollowUserError
from .workspace import UserWorkspace


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

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
        following_count = user.get_followings_count()
        followers_count = user.get_followers_count()
        posts_count = user.get_total_posts_count()

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

        interactions = database.get_user_interactions(
            profile_username=self.username, until_datetime=until_datetime
        )

        if len(interactions) == 0:
            logger.info('No Pygram followed users to unfollow. Quitting.')
            return

        pygram_user = InstagramUser(self.username)
        followers = set(pygram_user.get_followers())
        followings = set(pygram_user.get_followings())

        # Only keep users that don't follow back and that we are still following
        users_to_unfollow = {i.username for i in interactions if i.username not in followers}
        users_to_unfollow = users_to_unfollow & followings

        for user in users_to_unfollow:
            ig_user = InstagramUser(user)

            try:
                ig_user.unfollow()
            except UnfollowUserError as ex:
                logger.warning(f'Error trying to unfollow user {user}: {ex}. Skipping user.')
                continue
            else:
                self.unfollows_count += 1
                logger.info(
                    f'Unfollowed user {user} [{self.unfollows_count}/{len(users_to_unfollow)}]'
                )

                time.sleep(FOLLOW_USER_WAIT_TIME)

            if (
                self.unfollows_count > 0
                and self.unfollows_count % FOLLOW_COUNT_PAUSE_THRESHOLD == 0
            ):
                logger.info(
                    f'Unfollowed {FOLLOW_COUNT_PAUSE_THRESHOLD} users. '
                    + f'Sleeping for {FOLLOW_BREAK_WAIT_TIME}'
                )
                time.sleep(FOLLOW_BREAK_WAIT_TIME)
