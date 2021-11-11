"""Script that follows random followers of a particular user."""
import os

from dotenv import load_dotenv

from pygram import FollowParameters, Pygram


load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SOURCE_USERNAME = ""


if __name__ == "__main__":
    pygram = Pygram(USERNAME, PASSWORD)

    with pygram:
        pygram.follow_user_followers(
            SOURCE_USERNAME,
            amount=100,
            parameters=FollowParameters(
                min_posts_count=15,
                min_followers=100,
                min_followings=100,
                skip_business_accounts=True,
            ),
        )
