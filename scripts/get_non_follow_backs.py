"""Gets the list of users that a user follows but don't follow the user back.

Usage:

    python get_non_follow_backs.py someiguser
"""
import sys
import os

from dotenv import load_dotenv

from pygram import Pygram
from pygram.users import InstagramUser


load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


if __name__ == "__main__":
    username: str = sys.argv[1]

    pygram = Pygram(USERNAME, PASSWORD)

    with pygram:
        user = InstagramUser(username)
        followers = set(user.get_followers())
        followings = set(user.get_followings())

        result = followings - followers
        print(result)
