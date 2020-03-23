# Installation

```
pip install pygram
```

# Basic Usage

Using Pygram is incredibly simple:

```python
import datetime

from pygram import Pygram


session = Pygram('myusername', 'password')

with session:
    # Following user's followers
    pygram.follow_user_followers('iguser', amount=100)

    # Unfollowing all users that were followed until 5 days ago
    five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
    pygram.unfollow_users(until_datetime=five_days_ago)

```
