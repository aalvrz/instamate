from typing import Any

import httpx

from instamate.browser import get_browser


class GetUserDataQuery:
    """Issues a query to Instagram query service."""

    def __init__(self) -> None:
        browser = get_browser()
        browser_cookies: list[dict[str, Any]] = browser.get_cookies()

        # Inject the cookies contained in the browser into the HTTP client so that requests
        # can be correctly authorized
        self.cookies: dict[str, Any] = {
            cookie_dict["name"]: cookie_dict["value"] for cookie_dict in browser_cookies
        }

    def search_users(self, username: str) -> list[dict[str, Any]]:
        query_url = "https://www.instagram.com/web/search/topsearch/?query={username}"

        resp = httpx.get(query_url.format(username=username), cookies=self.cookies)
        resp_json = resp.json()

        return resp_json.get("users", [])

    def get_user_data(self, username: str) -> dict[str, Any]:
        user_data: dict[str, Any] = {}
        users_results = self.search_users(username)

        try:
            user_data = users_results[0].get("user", {})
        except IndexError:
            return {}

        if user_data.get("username") != username:
            return {}

        return user_data
