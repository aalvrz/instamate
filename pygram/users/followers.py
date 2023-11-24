from .base import UserList
from ..graphql import get_graphql_query_hash


class UserFollowers(UserList):
    """
    Iterable of a user's followers.
    """

    key_name = "edge_followed_by"

    def _get_query_hash(self):
        return get_graphql_query_hash()
