import json
import logging
import random
import time
from typing import Any

import httpx


# See: https://stackoverflow.com/questions/32407851/instagram-api-how-can-i-retrieve-the-list-of-people-a-user-is-following-on-ins
GET_FOLLOWERS_QUERY_HASH = "c76146de99bb02f6415203be841dd25a"
GET_FOLLOWINGS_QUERY_HASH = "d04b0a864b4b54837c0d870b0e77e076"

logger = logging.getLogger(__name__)


class GraphQLAPI:
    """Allows interacting with Instagram's GraphQL API."""

    base_graphql_query_url = (
        "https://www.instagram.com/graphql/query/?query_hash={query_hash}"
    )

    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def get_followers(self, user_id: str, randomize: bool | None = True) -> set[str]:
        logger.info("Obtaining followers for user '%s'" % user_id)

        followers = self._get_users(
            user_id, "edge_followed_by", GET_FOLLOWERS_QUERY_HASH, randomize
        )
        return followers

    def get_followings(self, user_id: str, randomize: bool | None = True) -> set[str]:
        logger.info("Obtaining followings for user '%s'" % user_id)

        followings = self._get_users(
            user_id, "edge_follow", GET_FOLLOWINGS_QUERY_HASH, randomize
        )
        return followings

    def _get_users(
        self, user_id: str, key: str, query_hash: str, randomize: bool | None = True
    ) -> set[str]:
        users: list[str] = []

        params = {
            "id": user_id,
            "include_reel": "true",
            "fetch_mutual": "true",
            "first": 50,
        }
        has_next_page = False

        while True:
            if has_next_page:
                time.sleep(random.randint(2, 6))

            users_data = self._get_page_data(params, key, query_hash)
            users_page: list[dict[str, Any]] = users_data["edges"]
            users_list: list[str] = [user["node"]["username"] for user in users_page]
            users.extend(users_list)

            has_next_page = users_data["page_info"]["has_next_page"]

            if not has_next_page:
                break

            end_cursor = users_data["page_info"]["end_cursor"]
            params["after"] = end_cursor

        if randomize:
            random.shuffle(users)

        return set(users)

    def _get_page_data(
        self, params: dict[str, Any], key: str, query_hash: str
    ) -> dict[str, Any]:
        url = self.base_graphql_query_url.format(
            query_hash=query_hash
        ) + f"&variables={json.dumps(params)}"

        logger.debug("Requesting new page '%s'" % url)

        response = self.client.get(url)
        data = response.json()

        users_data = data["data"]["user"][key]
        return users_data
