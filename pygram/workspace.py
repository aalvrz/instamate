import os
import pickle
from typing import Dict, List

from .exceptions import PygramException


DEFAULT_WORKSPACES_PATH = os.path.expanduser('~/Pygram')


class WorkspaceAlreadyExistsException(PygramException):
    """
    Raised when creating a workspace where the workspace folder already exists.
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
        self._cookie_path = os.path.join(
            self.path, f'{self._username}_cookie.pkl'
        )

    def create(self):
        """
        Creates the workspace directory using the path provided.
        """
        os.makedirs(self.path)

    def get_cookies(self) -> List[Dict]:
        """
        Searches for and returns available cookies from the workspace.
        """

        return [
            cookie
            for cookie in
            pickle.load(open(self._cookie_file_name, 'rb'))
        ]

    def store_cookies(self, cookies):
        """Store cookies in the user workspace."""
        pickle.dump(
            cookies,
            open(self._cookie_file_name, 'wb')
        )

    @property
    def exists(self):
        return os.path.isdir(self.path)
