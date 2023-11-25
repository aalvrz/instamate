import abc
import logging
import time

from ..browser import get_browser


logger = logging.getLogger(__name__)


class BaseInstagramPage(abc.ABC):
    link: str

    def __init__(self, *args, **kwargs):
        self.browser = get_browser()

    def go(self) -> None:
        get_browser().get(self.link)
        time.sleep(2)
        logger.info("Navigated to %s" % self.link)
