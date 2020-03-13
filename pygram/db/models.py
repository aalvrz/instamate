from peewee import CharField, Model


class Profile(Model):
    """Represents a profile that runs a Pygram session."""

    class Meta:
        database = None
        table_name = 'profiles'

    username = CharField(unique=True)
