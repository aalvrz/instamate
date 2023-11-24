from selenium import webdriver


FIREFOX_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) FxiOS/18.1 Mobile/16B92 Safari/605.1.15"
)

_CURRENT_BROWSER = None
DEFAULT_WINDOW_WIDTH = 375
DEFAULT_WINDOW_HEIGHT = 812


def get_browser():
    global _CURRENT_BROWSER

    if _CURRENT_BROWSER is None:
        options = webdriver.FirefoxOptions()

        # Set English language
        options.set_preference("intl.accept_languages", "en-US")
        options.set_preference("general.useragent.override", FIREFOX_USER_AGENT)

        # mute audio while watching stories
        options.set_preference("media.volume_scale", "0.0")

        _CURRENT_BROWSER = webdriver.Firefox(options=options)
        _CURRENT_BROWSER.set_window_size(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        return _CURRENT_BROWSER

    return _CURRENT_BROWSER
