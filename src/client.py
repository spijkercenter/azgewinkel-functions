import json
import os
from types import SimpleNamespace
from typing import Callable, Dict, TypeVar

import requests
from cachetools import cached, TTLCache
from requests.auth import HTTPBasicAuth

T = TypeVar("T")


class AZGewinkelClient:
    def __init__(self):
        key = os.environ.get("AZGEWINKEL_KEY")
        secret = os.environ.get("AZGEWINKEL_SECRET")
        self.__auth = HTTPBasicAuth(key, secret)
        self.root = "https://azgewinkel.ddns.net/wp-json/wc/v3"

    @cached(cache=TTLCache(maxsize=100, ttl=60))
    def get(self, path: str):

        response = requests.get(self.root + path, auth=self.__auth)
        if response.status_code != 200:
            raise IOError(response)
        text = response.text
        # pprint(json.loads(text))
        data = json.loads(text, object_hook=lambda d: SimpleNamespace(**d))
        if 'next' in response.links:
            next_path = response.links['next']['url']
            next_path = next_path.replace(self.root, "")
            next_data = self.get(next_path)
            data = data + next_data
        return data

    @cached(cache=TTLCache(maxsize=100, ttl=60))
    def load(self, path: str, mapper: Callable[[any], T]) -> Dict[int, T]:
        result = {}
        for item in self.get(path):
            result[item.id] = mapper(item)
        return result
