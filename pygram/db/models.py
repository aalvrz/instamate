import datetime

from peewee import CharField, DateTimeField, ForeignKeyField, IntegerField, Model


class Profile(Model):
    """Represents a profile that runs a Pygram session."""

    class Meta:
        database = None
        table_name = 'profiles'

    username = CharField(unique=True)


class Activity(Model):
    """Records activity of a Pygram session."""

    profile = ForeignKeyField(Profile, backref='activity')

    likes = IntegerField(default=0)
    comments = IntegerField(default=0)
    follows = IntegerField(default=0)
    unfollows = IntegerField(default=0)

    # Recorded when the session ends
    created_at = DateTimeField(default=datetime.datetime.now)


class AccountProgress(Model):
    """Records the progress over time of a Pygram user."""

    class Meta:
        table_name = 'accounts_progress'

    profile = ForeignKeyField(Profile, backref='account_progress')

    followers = IntegerField()
    following = IntegerField()
    total_posts = IntegerField()

    # Recorded at the start of the session
    created_at = DateTimeField(default=datetime.datetime.now)


class UserInteraction(Model):
    """
    Stores information about interactions with Instagram users.
    """

    class Meta:
        database_name = 'user_interactions'
        indexes = (
            (('profile_id', 'username'), True),
        )

    profile = ForeignKeyField(Profile, backref='user_interactions')

    username = CharField()
    followed_at = DateTimeField()
