import logging


INSTAMATE_LOG_FORMATTER = logging.Formatter(
    "[%(asctime)s] %(name)-5s %(levelname)s [%(username)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class InstamateLoggerContextFilter(logging.Filter):
    """Log filter that allows injecting current Instamate username context to log messages."""

    def __init__(self, username: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.username = username

    def filter(self, record):
        record.username = self.username
        return True
