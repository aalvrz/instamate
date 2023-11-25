import logging
import pickle
import os
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


def save_user_cookies(username: str, cookies: List[Dict[str, Any]]) -> None:
    """Saves a cookie in the local file system in Pickle format for a specific user."""

    with open(os.getcwd() + f"/cookies/{username}.pkl", "wb") as f:
        pickle.dump(cookies, f)


def load_user_cookies(username: str) -> List[Dict[str, Any]]:
    try:
        with open(os.getcwd() + f"/cookies/{username}.pkl", "rb") as f:
            cookies: List[Dict[str, Any]] = [cookie for cookie in pickle.load(f)]
    except FileNotFoundError:
        logger.warning("Unable to locate cookie file for user %s" % username)
        return []

    return cookies
