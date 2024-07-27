from django.db import models
from accounts_engine.models import BaseClass, CustomUser
import uuid


class Collection(BaseClass):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='collections')
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class Genre(BaseClass):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Movie(BaseClass):
    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class MovieGenre(BaseClass):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_genres')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='movie_genres')

    def __str__(self):
        return f"{self.movie.title} - {self.genre.name}"


class MovieCollection(BaseClass):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='movie_collections')
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='movie_collections')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_collections')

    class Meta:
        unique_together = ('user', 'collection', 'movie')

    def __str__(self):
        return f"{self.collection.title} - {self.movie.title}"
