from .auth import Authenticator
from .browser import PygramBrowserFactory
from .constants import INSTAGRAM_HOMEPAGE_URL
from .workspace import UserWorkspace


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

        self.browser = PygramBrowserFactory.firefox_browser()
        self.browser.implicitly_wait(5)

        self._login()

        return self

    def __exit__(self, type, value, traceback):
        self.browser.quit()

    def _create_user_workspace(self):
        if not self.workspace.exists:
            self.workspace.create()

    def _login(self):
        """
        Login the user using the crendetials provided.
        """

        self.browser.get(INSTAGRAM_HOMEPAGE_URL)

        authenticator = Authenticator(self.username, self.password, self.browser)
        authenticator.login()
