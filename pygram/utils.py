import datetime

from .constants import FOLLOW_BREAK_WAIT_TIME, FOLLOW_COUNT_PAUSE_THRESHOLD, FOLLOW_USER_WAIT_TIME


def get_follow_users_duration(amount: int) -> datetime.timedelta:
    """
    Calculate and return the approximate duration of following a certain amount of users

    :returns: a `timedelta` object that contains the following string representation: '2:30:00'
    """

    seconds = (FOLLOW_USER_WAIT_TIME * amount) + (
        (amount / FOLLOW_COUNT_PAUSE_THRESHOLD) * FOLLOW_BREAK_WAIT_TIME
    )

    return datetime.timedelta(seconds=seconds)
