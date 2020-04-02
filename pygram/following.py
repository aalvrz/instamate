"""Actions related to following users."""
import datetime
import logging
import time
from typing import Set

from .constants import FollowingStatus
from .db import get_database
from .users import InstagramUser


FOLLOW_USER_WAIT_TIME = 60
FOLLOW_BREAK_WAIT_TIME = 600
FOLLOW_COUNT_PAUSE_THRESHOLD = 20


logger = logging.getLogger('pygram.' + __name__)


class FollowParameters:
    """Parameters to determine if a user should be followed"""

    def __init__(
        self,
        min_posts_count: int = 0,
        min_followers: int = 0,
        min_followings: int = 0,
        skip_business_accounts: bool = False,
    ):
        self.min_posts_count = min_posts_count
        self.min_followers = min_followers
        self.min_followings = min_followings
        self.skip_business_accounts = skip_business_accounts

    def __str__(self):
        return 'Min posts: {0} | Min followers: {1} | Min followings: {2}'.format(
            self.min_posts_count, self.min_followers, self.min_followings
        )

    def should_follow(self, posts_count: int, followers_count: int, followings_count: int) -> bool:
        return (
            posts_count >= self.min_posts_count
            and followers_count >= self.min_followers
            and followings_count >= self.min_followings
        )


class FollowHandler:
    """
    Handler for following a list of users
    """

    def __init__(self, user: str, parameters: FollowParameters = None):
        """
        :param user: Username of the Pygram session user.
        :param parameters: Parameters that users to follow must satisfy in order to follow them.
        """

        self.user = user
        self.parameters = parameters

        self._follow_history = self._get_follow_history()

    def follow_users(self, users_to_follow: Set[str], amount: int) -> int:
        """
        Follow a list of users and return the amount of user's followed

        :param users_to_follow: List of users to follow
        :param amount: Maximum number of users to follow.
        """

        follows_count = 0

        logger.info(
            f'Starting to follow {amount} users. '
            f'This will take aprox. {self.get_follow_duration(amount)}'
        )

        if self.parameters:
            logger.info(f'Follow parameters: {self.parameters}')

        for username in users_to_follow:
            # Do not attempt to follow user's that have already been followed in the past using
            # Pygram
            if username in self._follow_history:
                continue

            ig_user = InstagramUser(username)

            if not self._user_satisfies_parameters(ig_user):
                logger.info(f'User {ig_user} does not pass parameters. Skipping.')
                time.sleep(3)
                continue

            following_status = ig_user.get_following_status(self.user)

            if following_status == FollowingStatus.NOT_FOLLOWING:
                ig_user.follow()

                follows_count += 1
                self._record_user_interaction(username)

                logger.info(f'Followed user {username} [{follows_count}/{amount}]')
                time.sleep(FOLLOW_USER_WAIT_TIME)
            else:
                logger.info(f'Skipping user {username} because follow status is {following_status}')
                time.sleep(3)

            if follows_count == amount:
                break

            if follows_count > 0 and follows_count % FOLLOW_COUNT_PAUSE_THRESHOLD == 0:
                logger.info(
                    f'Followed {FOLLOW_COUNT_PAUSE_THRESHOLD} users. '
                    + f'Sleeping for {FOLLOW_BREAK_WAIT_TIME}'
                )
                time.sleep(FOLLOW_BREAK_WAIT_TIME)

        return follows_count

    def _get_follow_history(self) -> Set[str]:
        follow_history = get_database().get_user_interactions(profile_username=self.user)
        return {i.username for i in follow_history}

    def _user_satisfies_parameters(self, ig_user: InstagramUser) -> bool:
        if self.parameters:
            if self.parameters.skip_business_accounts:
                if ig_user.is_business_account:
                    return False

            activity_counts = ig_user.get_all_activity_counts()
            if not self.parameters.should_follow(*activity_counts):
                return False

        return True

    def _record_user_interaction(self, username: str):
        get_database().record_user_interaction(
            profile_username=self.user, user_username=username, followed_at=datetime.datetime.now()
        )

    @staticmethod
    def get_follow_duration(amount: int) -> datetime.timedelta:
        """
        Calculate and return the approximate duration for following a certain amount of users

        :returns: a `timedelta` object that contains the following string representation: '2:30:00'
        """

        seconds = (FOLLOW_USER_WAIT_TIME * amount) + (
            (amount / FOLLOW_COUNT_PAUSE_THRESHOLD) * FOLLOW_BREAK_WAIT_TIME
        )

        return datetime.timedelta(seconds=seconds)
