"""Actions related to following users."""
import logging
from typing import Iterable, Sequence

from instamate.constants import FollowingStatus
from instamate.pages.profile import UnfollowUserError, UserProfilePage


logger = logging.getLogger(__name__)


def follow_users(users: Iterable[str], amount: int) -> None:
    """Navigates to the profile page of each user in a list of users and attempts to follow them."""

    if amount <= 0:
        raise ValueError("Invalid follow amount cap")

    follow_count = 0

    for username in users:
        user_page = UserProfilePage(username)
        user_page.go()

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


def unfollow_users(users: Sequence[str]) -> None:
    """Navigates to each user in a list of users and proceeds to unfollow them."""

    for username in users:
        user_page = UserProfilePage(username)
        user_page.go()

        following_status = user_page.get_following_status()

        if following_status != FollowingStatus.FOLLOWING:
            logger.warning(
                "You are not following '%s'. Skipping unfollow action." % username
            )
            continue

        try:
            user_page.unfollow()
        except UnfollowUserError:
            logger.error("Could not unfollow user '%s'" % username)
            continue

        logger.info("Unfollowed user '%s'" % username)

    logger.info("Finished unfollowing %d users" % len(users))
