"""Actions related to following users."""
import logging
import time
from typing import Iterable

from instamate.constants import FollowingStatus
from instamate.pages.profile import UserProfilePage


FOLLOW_USER_WAIT_TIME = 60
FOLLOW_BREAK_WAIT_TIME = 600
FOLLOW_COUNT_PAUSE_THRESHOLD = 20


logger = logging.getLogger(__name__)


def follow_users(users: Iterable[str], amount: int) -> None:
    if amount <= 0:
        raise ValueError("Invalid follow amount cap")

    follow_count = 0

    for username in users:
        user_page = UserProfilePage(username)
        user_page.go()

        time.sleep(3)

        following_status = user_page.get_following_status()

        if following_status != FollowingStatus.NOT_FOLLOWING:
            logger.info(
                "User %s is already being followed or requested. Skipping." % username
            )
            continue

        user_page.follow()
        follow_count += 1

        if follow_count >= amount:
            break

    logger.info("Finished following %d users" % follow_count)
