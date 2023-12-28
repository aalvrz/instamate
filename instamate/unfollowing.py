import datetime
import logging
import time
from typing import Set

from .following import (
    FOLLOW_USER_WAIT_TIME,
    FOLLOW_COUNT_PAUSE_THRESHOLD,
    FOLLOW_BREAK_WAIT_TIME,
)
from .pages.profile import UserProfilePage, UnfollowUserError


logger = logging.getLogger("instamate." + __name__)


class UnfollowHandler:
    """
    Handler for unfollowing Instagram users.

    Only users that have been followed through Instamate, and that DON'T follow back this account
    will be unfollowed.
    """

    def __init__(self, user: str, until_datetime: datetime.datetime = None):
        self.user = user
        self.until_datetime = until_datetime

        self._interactions = self._get_user_interactions()

    def unfollow_users(self) -> int:
        """Unfollow a list of users and return total number of unfollowed users."""

        if len(self._interactions) == 0:
            logger.info("No Instamate followed users to unfollow. Quitting.")
            return

        unfollows_count = 0
        users_to_unfollow = self._get_users_to_unfollow()

        for user in users_to_unfollow:
            ig_user = UserProfilePage(user)

            try:
                ig_user.unfollow()
            except UnfollowUserError as ex:
                logger.warning(
                    f"Error trying to unfollow user {user}: {ex}. Skipping user."
                )
                continue
            else:
                unfollows_count += 1
                logger.info(
                    f"Unfollowed user {user} [{unfollows_count}/{len(users_to_unfollow)}]"
                )

                time.sleep(FOLLOW_USER_WAIT_TIME)

            if (
                unfollows_count > 0
                and unfollows_count % FOLLOW_COUNT_PAUSE_THRESHOLD == 0
            ):
                logger.info(
                    f"Unfollowed {FOLLOW_COUNT_PAUSE_THRESHOLD} users. "
                    + f"Sleeping for {FOLLOW_BREAK_WAIT_TIME}"
                )
                time.sleep(FOLLOW_BREAK_WAIT_TIME)

        return unfollows_count

    def _get_user_interactions(self):
        return get_database().get_user_interactions(
            profile_username=self.user, until_datetime=self.until_datetime
        )

    def _get_users_to_unfollow(self) -> Set[str]:
        instamate_user = UserProfilePage(self.user)
        followers = set(instamate_user.get_followers())
        followings = set(instamate_user.get_followings())

        # Only keep users that don't follow back and that we are still following
        users_to_unfollow = {
            i.username for i in self._interactions if i.username not in followers
        }
        users_to_unfollow = users_to_unfollow & followings

        return users_to_unfollow
