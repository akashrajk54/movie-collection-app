# api_client.py

import requests
from requests.auth import HTTPBasicAuth


class APIClientFactory:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

    def create_client(self):
        return APIClient(self.base_url, self.username, self.password)


class APIClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

    def get(self, endpoint, params=None, timeout=5):
        url = f"{self.base_url}"
        print('url: => ', url)
        response = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth(self.username, self.password),
            timeout=timeout,
            verify=False
        )
        response.raise_for_status()
        return response.json()
