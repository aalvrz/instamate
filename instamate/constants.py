from enum import Enum


INSTAGRAM_HOMEPAGE_URL = "https://www.instagram.com"


class FollowingStatus(str, Enum):
    FOLLOWING = "Following"
    NOT_FOLLOWING = "Follow"
    REQUESTED = "Requested"
