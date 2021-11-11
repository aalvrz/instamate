"""Script that outputs common followers between two users."""
from pygram.users import InstagramUser

import os

from dotenv import load_dotenv

from pygram import FollowParameters, Pygram


load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


if __name__ == "__main__":
    pygram = Pygram(USERNAME, PASSWORD)

    with pygram:
        u1 = InstagramUser("someuser1")
        u1_followers = u1.get_followers()

        u2 = InstagramUser("someuser2")
        u2_followers = u2.get_followers()

        print("Common Followers:")
        print(set(u1_followers) & set(u2_followers))
