from .auth import Authenticator
from .browser import PygramBrowserFactory
from .constants import INSTAGRAM_HOMEPAGE_URL
from .workspace import UserWorkspace


class Pygram:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        self.workspace = UserWorkspace(self.username)
        self._create_user_workspace()

        self.browser = PygramBrowserFactory.firefox_browser()

        self.browser.implicitly_wait(5)
        self.browser.get(INSTAGRAM_HOMEPAGE_URL)

        self._login()

    def _create_user_workspace(self):
        if not self.workspace.exists:
            self.workspace.create()

    def _login(self):
        """
        Login the user using the crendetials provided.
        """
        authenticator = Authenticator(self.username, self.password, self.browser)
        authenticator.login()
