# from rest_framework import serializers
# from .models import MovieCollection, Collection, Movie, Genre, MovieGenre
#
#
# class CollectionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Collection
#         fields = '__all__'
#
#     def create(self, validated_data):
#         return super().create(validated_data)


from rest_framework import serializers
from .models import Collection, Movie, Genre, MovieGenre

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
        fields = ['uuid', 'title', 'description', 'movies']

    def get_movies(self, obj):
        movies = Movie.objects.filter(movie_collections__collection=obj)
        return MovieSerializer(movies, many=True).data

