"""Gets the list of users that a user follows but don't follow the user back.

Usage:

    python get_non_follow_backs.py someiguser
"""
import sys
import os

from dotenv import load_dotenv

from pygram import Pygram


load_dotenv()


if __name__ == "__main__":
    ig_username = os.getenv("INSTAGRAM_USERNAME")
    ig_password = os.getenv("INSTAGRAM_PASSWORD")

    if not ig_username or not ig_password:
        raise ValueError("Invalid Instagram username or password")

    try:
        username: str = sys.argv[1]
    except IndexError:
        raise ValueError("You must provide an Instagram username to get data from")

    with Pygram(ig_password, ig_password) as pygram:
        followers = pygram.get_user_followers(username)
        followings = pygram.get_user_followings(username)

    results = followings - followers
    print(results)
