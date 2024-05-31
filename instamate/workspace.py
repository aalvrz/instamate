import logging
import pickle
import os
from typing import Any


logger = logging.getLogger(__name__)


class Workspace:
    """Represents the local workspace directory in the user's local machine.

    By default the workspace directory will be created within the user's home directory.
    """

    DIR_NAME = ".instamate"

    def __init__(self, username: str) -> None:
        self.username = username
        self.path = os.path.join(os.environ["HOME"], self.DIR_NAME)

        self._create_workspace_dir()
        self.cookies_file_path = self._create_cookies_dir()

    def _create_workspace_dir(self):
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

    def _create_cookies_dir(self) -> str:
        cookies_dir = os.path.join(self.path, "cookies")
        try:
            os.mkdir(cookies_dir)
        except FileExistsError:
            pass

        cookies_file_path = os.path.join(cookies_dir, f"{self.username}.pkl")
        return cookies_file_path

    def save_user_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Saves a cookie in the local file system in Pickle format for a specific user."""

        with open(self.cookies_file_path, "w+b") as f:
            pickle.dump(cookies, f)

        logger.info("Saved cookies for user")

    def load_user_cookies(self) -> list[dict[str, Any]]:
        try:
            with open(self.cookies_file_path, "rb") as f:
                cookies: list[dict[str, Any]] = [cookie for cookie in pickle.load(f)]
        except FileNotFoundError:
            logger.warning("Unable to locate cookie file")
            return []

        logger.info("Loaded cookies")
        return cookies

    def __repr__(self):
        return f"Workspace({self.path})"
