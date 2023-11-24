from .base import UserList


class UserFollowings(UserList):
    """
    Iterable of a user's followings.
    """

    key_name = "edge_follow"

    def _get_query_hash(self):
        return "58712303d941c6855d4e888c5f0cd22f"
