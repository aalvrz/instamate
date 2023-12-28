"""Script that unfollows users that don't follow back the authenticated user."""
import datetime
import os

from dotenv import load_dotenv

from instamate import Instamate


load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


if __name__ == "__main__":
    with Instamate(USERNAME, PASSWORD) as instamate:
        five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
        instamate.unfollow_users()
