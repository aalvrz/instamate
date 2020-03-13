import os
import pickle
from typing import Dict, List, Set

from .exceptions import PygramException


DEFAULT_WORKSPACES_PATH = os.path.expanduser('~/Pygram')


class WorkspaceAlreadyExistsException(PygramException):
    """
    Raised when creating a workspace where the workspace folder already exists.
    """


class CookiesFileNotFoundError(PygramException):
    """
    Raised when trying to load cookies from file but file does not exist.
    """


class UserWorkspace:
    """
    A Instagram user workspace where session cookies and interaction data
    is stored.

    User workspaces are named after the user's username/handle.
    """

    def __init__(self, username):
        self._username = username

        self.path = os.path.join(DEFAULT_WORKSPACES_PATH, self._username)
        self._cookie_path = os.path.join(self.path, f'{self._username}_cookie.pkl')

        self._follow_history_path = os.path.join(self.path, 'follow_history.txt')

    def create(self):
        """
        Creates the workspace directory using the path provided.
        """
        os.makedirs(self.path)

    def get_cookies(self) -> List[Dict]:
        """
        Searches for and returns available cookies from the workspace.
        """

        try:
            cookies = [cookie for cookie in pickle.load(open(self._cookie_path, 'rb'))]
        except FileNotFoundError:
            raise CookiesFileNotFoundError

        return cookies

    def store_cookies(self, cookies):
        """Store cookies in the user workspace."""
        pickle.dump(cookies, open(self._cookie_path, 'wb'))

    def get_follow_history(self) -> Set[str]:
        history = set()

        try:
            with open(self._follow_history_path) as f:
                history = set(f.read().splitlines())
        except FileNotFoundError:
            pass

        return history

    def store_follow_history(self, follow_history: Set[str]):
        with open(self._follow_history_path, 'w') as f:
            f.write('\n'.join(follow_history))

    @property
    def exists(self):
        return os.path.isdir(self.path)
