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
