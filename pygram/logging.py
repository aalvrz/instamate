import logging


PYGRAM_LOG_FORMATTER = logging.Formatter(
    '[%(asctime)s] %(name)-5s %(levelname)s [%(username)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


class PygramLoggerContextFilter(logging.Filter):
    """
    Log filter that allows injecting current Pygram username context to log messages.
    """

    def __init__(self, username: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username

    def filter(self, record):
        record.username = self.username
        return True
