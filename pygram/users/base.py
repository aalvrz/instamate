import abc
import itertools
import json
import random
import time
from typing import List, Set

from ..browser import get_browser


class UserList(abc.ABC):
    """
    Base class that represents a list of Instagram users, either followers or followings.

    Clases that extend this base class should have a class variable ``key_name`` so that the
    subclass knows which key to access from the response data in order to obtain the desired
    data.

    Each request to Instagram for obtaining usernames returns around 50 users. Users are always
    returned in the same order, so in order to obtain good randomization, all users need to be
    fetched first. This can take a considerable amount of time.

    Fetching of users is done immediately in initialization.
    """

    def __init__(self, user_id: int, randomize: bool = True):
        self._user_id = user_id
        self._randomize = randomize

        self._users = self._get_users()

    def _get_users(self) -> Set[str]:
        users = []

        def _get_data(params) -> (List[str]):
            url = f'{self._get_graphql_query_url()}&variables={json.dumps(params)}'
            get_browser().get(url)

            pre_element = get_browser().find_element_by_tag_name('pre')
            data = json.loads(pre_element.text)

            users_data = data['data']['user'][self.key_name]
            return users_data

        params = {'id': self._user_id, 'include_reel': 'true', 'fetch_mutual': 'true', 'first': 50}
        has_next_page = False

        while True:
            if has_next_page:
                time.sleep(random.randint(2, 6))

            users_data = _get_data(params)
            users_page = users_data['edges']
            users_list = [user['node']['username'] for user in users_page]

            users.append(users_list)

            has_next_page = users_data['page_info']['has_next_page']

            if not has_next_page:
                break

            end_cursor = users_data['page_info']['end_cursor']
            params['after'] = end_cursor

        users = list(itertools.chain.from_iterable(users))

        if self._randomize:
            random.shuffle(users)

        return set(users)

    def _get_graphql_query_url(self) -> str:
        return f'view-source:https://www.instagram.com/graphql/query/?query_hash={self._get_query_hash()}'

    def __iter__(self):
        yield from self._users

    def __len__(self):
        return len(self._users)

    @abc.abstractmethod
    def _get_query_hash(self) -> str:
        pass
