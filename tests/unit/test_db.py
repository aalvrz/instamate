import pytest

from pygram.db import PygramDatabase
from pygram.db.models import AccountProgress, Activity, Profile


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
