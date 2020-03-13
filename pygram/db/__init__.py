import os

from peewee import SqliteDatabase

from .models import Profile
from ..workspace import DEFAULT_WORKSPACES_PATH


DATABASE_PATH = os.path.join(DEFAULT_WORKSPACES_PATH, 'pygram.db')
MODELS = (Profile,)

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

    def close(self):
        self.db.close()


def get_database() -> PygramDatabase:
    global _DATABASE
    if _DATABASE is None:
        _DATABASE = PygramDatabase()

    return _DATABASE
