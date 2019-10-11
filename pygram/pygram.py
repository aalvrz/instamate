import logging

from .auth import Authenticator, AuthenticationError
from .browser import get_browser
from .constants import INSTAGRAM_HOMEPAGE_URL
from .users import InstagramUser
from .workspace import UserWorkspace


logging.basicConfig()
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

        get_browser().get(INSTAGRAM_HOMEPAGE_URL)

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
