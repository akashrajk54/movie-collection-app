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


#
# from movies.models import MovieCollection, Collection, Movie, Genre, MovieGenre
# from rest_framework.exceptions import ValidationError
#
#
# class MovieCollectionService:
#     @staticmethod
#     def create_collection_with_movies(user, collection_data, movies_data):
#         # Create the collection
#         collection = Collection.objects.create(
#             title=collection_data['title'],
#             description=collection_data['description'],
#             user=user
#         )
#
#         # Process movies data
#         for movie_data in movies_data:
#             movie_uuid = movie_data.get('uuid')
#             movie, created = Movie.objects.get_or_create(uuid=movie_uuid, defaults={
#                 'title': movie_data.get('title'),
#                 'description': movie_data.get('description')
#             })
#
#             if created:
#                 # If the movie is created, we need to link genres
#                 genre_names = movie_data.get('genres', '').split(',')
#                 for genre_name in genre_names:
#                     genre, _ = Genre.objects.get_or_create(name=genre_name.strip())
#                     MovieGenre.objects.get_or_create(movie=movie, genre=genre)
#
#             # Add movie to the collection
#             MovieCollection.objects.get_or_create(user=user, collection=collection, movie=movie)
#
#         return collection


