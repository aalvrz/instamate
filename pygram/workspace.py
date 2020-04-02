import logging
import os
import pickle
from typing import Dict, List

from .exceptions import PygramException
from .logging import PYGRAM_LOG_FORMATTER


DEFAULT_WORKSPACES_PATH = os.path.expanduser('~/Pygram')


logger = logging.getLogger('pygram')


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
        self._create()

        self._cookie_path = os.path.join(self.path, f'{self._username}_cookie.pkl')

        self._setup_file_logger()

    def _create(self):
        """
        Creates the workspace directory using the path provided.
        """

        if not self.exists:
            os.makedirs(self.path)

    def _setup_file_logger(self):
        """Adds additional logging to a log file in the user workspace."""

        handler = logging.FileHandler(os.path.join(self.path, 'logs.txt'))
        handler.setFormatter(PYGRAM_LOG_FORMATTER)

        # Multiple instantiations of a `UserWorkspace` will result in repeated additions of
        # FileHandlers. Therefore check if a FileHandler already exists
        if any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
            logger.addHandler(handler)

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

    @property
    def exists(self):
        return os.path.isdir(self.path)
