from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.webdriver import FirefoxProfile


FIREFOX_USER_AGENT = (
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 '
    '(KHTML, like Gecko) FxiOS/18.1 Mobile/16B92 Safari/605.1.15'
)
_CURRENT_BROWSER = None


def get_browser():
    global _CURRENT_BROWSER
    if _CURRENT_BROWSER is None:
        _CURRENT_BROWSER = PygramFirefoxBrowser()

    return _CURRENT_BROWSER


class PygramFirefoxBrowser(WebDriver):
    """
    Selenium FireFox web driver with special settings.
    """

    def __init__(self, *args, **kwargs):
        firefox_profile = FirefoxProfile()

        # Set English language
        firefox_profile.set_preference('intl.accept_languages', 'en-US')
        firefox_profile.set_preference('general.useragent.override', FIREFOX_USER_AGENT)

        # mute audio while watching stories
        firefox_profile.set_preference('media.volume_scale', '0.0')

        super().__init__(firefox_profile=firefox_profile, *args, **kwargs)

        # Set mobile viewport (iPhone X)
        self.set_window_size(375, 812)

    def navigate(self, url: str):
        """Navigates to a URL if the current page is not on that URL."""

        assert 'instagram.com' in url

        # NOTE: `url` must include the www subdomain
        if url not in self.current_url:
            self.get(url)
