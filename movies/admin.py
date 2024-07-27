from django.contrib import admin
from movies.models import Collection, Genre, Movie, MovieGenre, MovieCollection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'description')
    search_fields = ('title', 'user__username', 'description')
    list_filter = ('user',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')


@admin.register(MovieGenre)
class MovieGenreAdmin(admin.ModelAdmin):
    list_display = ('movie', 'genre')
    search_fields = ('movie__title', 'genre__name')
    list_filter = ('genre',)


@admin.register(MovieCollection)
class MovieCollectionAdmin(admin.ModelAdmin):
    list_display = ('collection', 'movie', 'user')
    search_fields = ('collection__title', 'movie__title', 'user__username')
    list_filter = ('collection', 'user')
