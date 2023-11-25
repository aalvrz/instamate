from enum import Enum


INSTAGRAM_HOMEPAGE_URL = "https://www.instagram.com"

MEDIA_PHOTO = "photo"
MEDIA_VIDEO = "video"
MEDIA_CAROUSEL_ = "carousel"


class FollowingStatus(str, Enum):
    FOLLOWING = "Following"
    NOT_FOLLOWING = "Follow"
    REQUESTED = "Requested"
