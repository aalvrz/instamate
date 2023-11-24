import datetime
import os

from peewee import SqliteDatabase

from .models import AccountProgress, Activity, Profile, UserInteraction
from ..workspace import DEFAULT_WORKSPACES_PATH


DATABASE_PATH = os.path.join(DEFAULT_WORKSPACES_PATH, "pygram.db")
MODELS = (Profile, Activity, AccountProgress, UserInteraction)

_DATABASE = None


class PygramDatabase:
    """
    Pygram local database

    The local Pygram database keeps record of activity done per Pygram session for each user
    authenticated in the session.
    """

    database_backend = SqliteDatabase

    def __init__(self, database_path=None):
        database_path = database_path or ":memory:"

        self.db = self.database_backend(database_path)
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

    def record_account_progress(
        self,
        username: str,
        followers_count: int,
        following_count: int,
        total_posts_count: int,
    ):
        profile = Profile.get(Profile.username == username)

        AccountProgress.create(
            profile=profile,
            followers=followers_count,
            following=following_count,
            total_posts=total_posts_count,
        )

    def record_user_interaction(
        self, profile_username: str, user_username: str, followed_at: datetime.datetime
    ):
        """
        Records an interaction (such as following) with an Instagram user
        """

        profile = Profile.get(Profile.username == profile_username)

        UserInteraction.get_or_create(
            profile=profile, username=user_username, followed_at=followed_at
        )

    def get_user_interactions(
        self, profile_username: str, until_datetime: datetime.datetime = None
    ):
        interactions = (
            UserInteraction.select()
            .join(Profile)
            .where(Profile.username == profile_username)
        )

        if until_datetime:
            interactions = interactions.where(
                UserInteraction.followed_at <= until_datetime
            )

        return interactions

    def close(self):
        self.db.close()


def get_database() -> PygramDatabase:
    global _DATABASE
    if _DATABASE is None:
        _DATABASE = PygramDatabase(DATABASE_PATH)

    return _DATABASE
