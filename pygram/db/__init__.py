import os

from peewee import SqliteDatabase

from .models import Activity, Profile
from ..workspace import DEFAULT_WORKSPACES_PATH


DATABASE_PATH = os.path.join(DEFAULT_WORKSPACES_PATH, 'pygram.db')
MODELS = (Profile, Activity)

_DATABASE = None


class PygramDatabase:
    """
    Pygram local database

    The local Pygram database keeps record of activity done per Pygram session for each user
    authenticated in the session.
    """

    database_backend = SqliteDatabase

    def __init__(self):
        self.db = self.database_backend(DATABASE_PATH)
        self.db.connect()

        self._bind_models()
        self._create_tables()

    def _bind_models(self):
        self.db.bind(MODELS)

    def _create_tables(self):
        self.db.create_tables(MODELS)

    def create_profile(self, username: str):
        """Register a profile record for the current session if it doesn't exist."""

        Profile.get_or_create(username=username)

    def record_activity(
        self,
        username: str,
        likes_count: int = 0,
        comments_count: int = 0,
        follows_count: int = 0,
        unfollows_count: int = 0,
    ):
        """
        Records activity data of a session.

        :param username: Username of the user running the session.
        """

        profile = Profile.get(Profile.username == username)

        Activity.create(
            profile=profile,
            likes=likes_count,
            comments=comments_count,
            follows=follows_count,
            unfollows=unfollows_count,
        )

    def close(self):
        self.db.close()


def get_database() -> PygramDatabase:
    global _DATABASE
    if _DATABASE is None:
        _DATABASE = PygramDatabase()

    return _DATABASE
