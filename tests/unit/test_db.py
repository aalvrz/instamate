import datetime

import pytest
from faker import Faker
from peewee import IntegrityError

from pygram.db import PygramDatabase
from pygram.db.models import AccountProgress, Activity, Profile, UserInteraction


fake = Faker()


@pytest.fixture
def database() -> PygramDatabase:
    return PygramDatabase()


@pytest.fixture
def profile() -> Profile:
    profile = Profile.create(username='champaignepapi')
    return profile


class TestPygramDatabase:
    def test_create_profile(self, database):
        assert Profile.select().count() == 0

        username = 'sandman23'
        database.create_profile(username)

        qs = Profile.select().where(Profile.username == username)

        assert len(qs) == 1
        assert qs[0].username == username

    def test_record_activity(self, database, profile):
        assert Activity.select().count() == 0

        database.record_activity(username=profile.username, follows_count=54)

        qs = Activity.select().where(Activity.profile == profile)

        assert len(qs) == 1
        assert qs[0].follows == 54

    def test_record_account_progress(self, database, profile):
        assert AccountProgress.select().count() == 0

        database.record_account_progress(
            username=profile.username, followers_count=45, following_count=100, total_posts_count=50
        )

        progress_qs = AccountProgress.select().where(AccountProgress.profile == profile)
        assert len(progress_qs) == 1

        assert progress_qs[0].followers == 45
        assert progress_qs[0].following == 100
        assert progress_qs[0].total_posts == 50

    def test_record_user_interaction(self, database, profile):
        assert UserInteraction.select().count() == 0

        user_username = 'jizz332'
        followed_at = datetime.datetime.now()

        database.record_user_interaction(
            profile_username=profile.username, user_username=user_username, followed_at=followed_at
        )

        interaction_qs = UserInteraction.select().where(
            UserInteraction.profile == profile, UserInteraction.username == user_username
        )

        assert len(interaction_qs) == 1
        assert interaction_qs[0].followed_at == followed_at

        # Test unique together constraint
        with pytest.raises(IntegrityError):
            UserInteraction.create(
                profile_username=profile.username,
                user_username=user_username,
                followed_at=followed_at,
            )

    def test_get_user_interactions(self, database, profile):
        usernames = ['supab1tch', 'distroboss12']
        for username in usernames:
            database.record_user_interaction(
                profile_username=profile.username,
                user_username=username,
                followed_at=datetime.datetime.now(),
            )

        interactions = database.get_user_interactions(profile_username=profile.username)

        assert usernames == [i.username for i in interactions]
