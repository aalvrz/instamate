# Installation

```
pip install pygram
```

## Installing a web driver

You will need to install a web driver such as [Geckodriver](https://github.com/mozilla/geckodriver/releases). Simply download a release binary and place it in your file system at `/usr/local/bin`.

# Configuration

Create a `.env` file with your instagram authentication credentials:

```
INSTAGRAM_USERNAME="myuser"
INSTAGRAM_PASSWORD="foobar"
```

# Basic Usage

Using Pygram is incredibly simple:

```python
import datetime

from pygram import Pygram


pygram = Pygram('myusername', 'password')

with pygram:
    # Following user's followers
    pygram.follow_user_followers('iguser', amount=100)

    # Unfollowing all users that were followed until 5 days ago
    five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
    pygram.unfollow_users(until_datetime=five_days_ago)

```

### Limiting which users to follow

Parameters can be provided to indicate which users to follow:

```python
from pygram import FollowParameters, Pygram


with pygram:
    pygram.follow_user_followers(
        'user1',
        amount=100,
        parameters=FollowParameters(
            min_posts_count=100,
            min_followers=200,
            min_followings=300,
        )
    )
```

## Troubleshooting

- https://stackoverflow.com/questions/72405117/selenium-geckodriver-profile-missing-your-firefox-profile-cannot-be-loaded
