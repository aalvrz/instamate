"""
Pygram - The Python bot for Instagram


Commands:

    - `follow_user_followers: Obtains the list of followers of a specific user
                              and follows them.
"""
import logging
import sys
import time

from .auth import Authenticator, AuthenticationError
from .browser import get_browser
from .constants import INSTAGRAM_HOMEPAGE_URL, FollowingStatus
from .users import InstagramUser
from .workspace import UserWorkspace


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class Pygram:
    """
    Initializes a Pygram session.
    """

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def __enter__(self):
        self.workspace = UserWorkspace(self.username)
        self._create_user_workspace()

        get_browser().implicitly_wait(5)

        self._login()

        return self

    def __exit__(self, type, value, traceback):
        get_browser().quit()

    def _create_user_workspace(self):
        if not self.workspace.exists:
            self.workspace.create()

    def _login(self):
        """
        Login the user using the crendetials provided.
        """

        get_browser().navigate(INSTAGRAM_HOMEPAGE_URL)

        authenticator = Authenticator(self.username, self.password)
        try:
            authenticator.login()
        except AuthenticationError as ex:
            logger.error(f'Error while trying to log in: {ex}')
            return

        logger.info('Logged in successfully.')

    def get_user_followers(self, username: str) -> int:
        user = InstagramUser(username)
        return user.get_followers()

    def follow_user_followers(self, username: str):
        """
        Obtains the list of followers of a specific user and follows them.
        """

        logger.info(f"Obtaining {username}'s followers.")
        user = InstagramUser(username)
        user_followers = user.get_followers(randomize=True)

        for follower_username in user_followers:
            ig_follower = InstagramUser(follower_username)
            following_status = ig_follower.get_following_status(self.username)

            if following_status == FollowingStatus.NOT_FOLLOWING:
                ig_follower.follow()
                logger.info(f'Followed user {follower_username}')

                time.sleep(60)
            else:
                logger.info(
                    f'Skipping user {follower_username} because follow status is {following_status}'
                )

        logger.info(f"Finished following {username}'s followers")
