from .base import UserList
from ..graphql import get_graphql_query_hash


class UserFollowers(UserList):
    """
    Iterable of a user's followers.
    """

    key_name = 'edge_followed_by'

    def _get_query_hash(self):
        return get_graphql_query_hash()


class FollowParameters:
    """Parameters to determine if a user should be followed"""

    def __init__(self, min_posts_count: int = 0, min_followers: int = 0, min_followings: int = 0):
        self.min_posts_count = min_posts_count
        self.min_followers = min_followers
        self.min_followings = min_followings

    def __str__(self):
        return 'Min posts: {0} | Min followers: {1} | Min followings: {2}'.format(
            self.min_posts_count,
            self.min_followers,
            self.min_followings
        )

    def should_follow(self, posts_count: int, followers_count: int, followings_count: int) -> bool:
        return (
            posts_count >= self.min_posts_count
            and followers_count >= self.min_followers
            and followings_count >= self.min_followings
        )
