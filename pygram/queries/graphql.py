import json
import logging
import random
import time
from typing import Any, Dict, List, Optional, Set

import httpx


GET_FOLLOWERS_QUERY_HASH = "c76146de99bb02f6415203be841dd25a"
GET_FOLLOWINGS_QUERY_HASH = "d04b0a864b4b54837c0d870b0e77e076"

logger = logging.getLogger(__name__)


class GraphQLAPI:
    """Allows interacting with Instagram's GraphQL API."""

    base_graphql_query_url = (
        "https://www.instagram.com/graphql/query/?query_hash={query_hash}"
    )

    def __init__(self, client: httpx.Client):
        self.client = client

    def get_followers(self, user_id: str, randomize: Optional[bool] = True) -> Set[str]:
        followers = self._get_users(
            user_id, "edge_followed_by", GET_FOLLOWERS_QUERY_HASH, randomize
        )
        return followers

    def get_followings(
        self, user_id: str, randomize: Optional[bool] = True
    ) -> Set[str]:
        followings = self._get_users(
            user_id, "edge_follow", GET_FOLLOWINGS_QUERY_HASH, randomize
        )
        return followings

    def _get_users(
        self, user_id: str, key: str, query_hash: str, randomize: Optional[bool] = True
    ) -> Set[str]:
        followers: List[str] = []

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
            users_page: List[Dict[str, Any]] = users_data["edges"]
            users_list: List[str] = [user["node"]["username"] for user in users_page]
            followers.extend(users_list)

            has_next_page = users_data["page_info"]["has_next_page"]

            if not has_next_page:
                break

            end_cursor = users_data["page_info"]["end_cursor"]
            params["after"] = end_cursor

        if randomize:
            random.shuffle(followers)

        return set(followers)

    def _get_page_data(
        self, params: Dict[str, Any], key: str, query_hash: str
    ) -> Dict[str, Any]:
        url = self.base_graphql_query_url.format(
            query_hash=query_hash
        ) + f"&variables={json.dumps(params)}"

        logger.info("Requesting new page '%s'" % url)

        response = self.client.get(url)
        data = response.json()

        users_data = data["data"]["user"][key]
        return users_data
