import abc
import logging
import time

from ..browser import get_browser


logger = logging.getLogger(__name__)


class BaseInstagramPage(abc.ABC):
    """Interface representing an Instagram web page that can be navigated to in the browser."""

    link: str

    def __init__(self, *args, **kwargs) -> None:
        self.browser = get_browser()

    def go(self) -> None:
        get_browser().get(self.link)
        time.sleep(2)
        logger.info("Navigated to %s" % self.link)

    def __str__(self):
        return self.link

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.link})>"
