from django.core.cache import cache
from retry import retry
from movies.config import ConfigSingleton
from movies.api_client import APIClientFactory
from movies.models import Collection, Movie, Genre, MovieGenre, MovieCollection
from django.db import transaction
from rest_framework.exceptions import NotFound


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


@transaction.atomic
class MovieCollectionService:
    def __init__(self, user, collection):
        self.user = user
        self.collection = collection

    def save_movies_and_link_genres(self, movies_data):
        """
        Save movies and link genres.
        """
        for movie_data in movies_data:
            movie_uuid = movie_data.get('uuid')
            movie, created = Movie.objects.get_or_create(uuid=movie_uuid, defaults={
                'title': movie_data.get('title'),
                'description': movie_data.get('description')
            })

            if created:
                # If the movie is created, we need to link genres
                genre_names = movie_data.get('genres', '').split(',')
                for genre_name in genre_names:
                    genre, _ = Genre.objects.get_or_create(name=genre_name.strip())
                    MovieGenre.objects.get_or_create(movie=movie, genre=genre)

            # Add movie to the collection
            MovieCollection.objects.get_or_create(user=self.user, collection=self.collection, movie=movie)


class CollectionUpdateService:

    @staticmethod
    def update_collection_and_movies(user, collection_uuid, data):
        try:
            collection = Collection.objects.get(uuid=collection_uuid, user=user)
        except Collection.DoesNotExist:
            raise NotFound("Collection not found.")

        # Update collection details
        collection.title = data.get('title', collection.title)
        collection.description = data.get('description', collection.description)
        collection.save()

        # Update movies in the collection
        movies_data = data.get('movies', [])
        for movie_data in movies_data:
            movie_uuid = movie_data.get('uuid')
            movie, created = Movie.objects.get_or_create(uuid=movie_uuid, defaults={
                'title': movie_data.get('title'),
                'description': movie_data.get('description')
            })

            if created:
                # Link genres if the movie is newly created
                genre_names = movie_data.get('genres', '').split(',')
                for genre_name in genre_names:
                    genre, _ = Genre.objects.get_or_create(name=genre_name.strip())
                    MovieGenre.objects.get_or_create(movie=movie, genre=genre)

            # Check if the movie is already in the collection
            if not MovieCollection.objects.filter(collection=collection, movie=movie).exists():
                MovieCollection.objects.create(user=user, collection=collection, movie=movie)

        return collection
