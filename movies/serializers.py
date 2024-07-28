from rest_framework import serializers
from .models import Collection, Movie, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['uuid', 'title', 'description', 'genres']

    def get_genres(self, obj):
        genres = obj.movie_genres.select_related('genre').all()
        return [genre.genre.name for genre in genres]


class CollectionSerializer(serializers.ModelSerializer):
    movies = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ['uuid', 'user', 'title', 'description', 'movies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        action = self.context.get('view').action if self.context.get('view') else None

        if request and request.method == 'GET':
            if action == 'list':
                # Exclude 'user' and 'movies' fields for list action
                self.fields.pop('user')
                self.fields.pop('movies')
            elif action == 'retrieve':
                # Exclude 'user' and 'uuid' fields for retrieve action
                self.fields.pop('user')
                self.fields.pop('uuid')

    def get_movies(self, obj):
        movies = Movie.objects.filter(movie_collections__collection=obj)
        return MovieSerializer(movies, many=True).data
