"""Script that outputs common followers between two users."""
import os
import sys

from dotenv import load_dotenv

from instamate import Instamate


load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


if __name__ == "__main__":
    with Instamate(USERNAME, PASSWORD) as instamate:
        try:
            user1 = sys.argv[1]
            user2 = sys.argv[2]
        except IndexError:
            raise ValueError("You must provide two Instagram usernames to get data from")

        user1_followers = instamate.get_user_followers(user1)
        user2_followers = instamate.get_user_followers(user2)

        print("Common Followers:")
        print(user1_followers & user2_followers)
