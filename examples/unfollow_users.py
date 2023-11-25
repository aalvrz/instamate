"""Script that unfollows users that don't follow back the authenticated user."""
import datetime
import os

from dotenv import load_dotenv

from pygram import Pygram


load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


if __name__ == "__main__":
    pygram = Pygram(USERNAME, PASSWORD)

    with pygram:
        five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
        pygram.unfollow_users()
