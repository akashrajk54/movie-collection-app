# movie_service.py

from django.core.cache import cache
from retry import retry
from movies.config import ConfigSingleton
from movies.api_client import APIClientFactory


class MovieService:
    def __init__(self):
        self.config = ConfigSingleton()
        self.api_client = APIClientFactory(
            self.config.MOVIE_API_URL,
            self.config.MOVIE_API_USERNAME,
            self.config.MOVIE_API_PASSWORD
        ).create_client()

    @retry(tries=3, delay=2, backoff=2)
    def fetch_movies(self, page=1):
        cache_key = f'movies_page_{page}'
        data = cache.get(cache_key)

        if not data:
            data = self.api_client.get('movies', params={'page': page})
            cache.set(cache_key, data, timeout=300)  # Cache for 5 minutes

        return data
