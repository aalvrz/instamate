import os
import sys

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

    with Pygram(ig_username, ig_password) as pygram:
        pygram.follow_user_followers(username)
