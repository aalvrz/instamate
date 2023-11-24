from enum import Enum


INSTAGRAM_HOMEPAGE_URL = "https://www.instagram.com"

MEDIA_PHOTO = "photo"
MEDIA_VIDEO = "video"
MEDIA_CAROUSEL_ = "carousel"


class FollowingStatus(Enum):
    FOLLOWING = 1
    NOT_FOLLOWING = 2
    REQUESTED = 3

    @classmethod
    def get_following_status_from_string(cls, value: str):
        if value == "Message":
            return cls.FOLLOWING
        elif value == "Requested":
            return cls.REQUESTED

        return cls.NOT_FOLLOWING
