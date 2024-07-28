import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from movies.models import Collection, Movie, Genre
from movies.factories import UserFactory, CollectionFactory, MovieFactory, GenreFactory


@pytest.mark.django_db
class TestMovieCollectionViewSet:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_create_collection(self):
        genre = GenreFactory()
        movie = MovieFactory()
        data = {
            "title": "My Collection",
            "description": "My favorite movies",
            "movies": [{"uuid": str(movie.uuid), "title": movie.title, "description": movie.description, "genres": genre.name}]
        }
        url = reverse('movie-collection-list')

        response = self.client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Collection.objects.count() == 1
        assert Collection.objects.first().title == "My Collection"

    def test_list_collections(self):
        CollectionFactory(user=self.user)
        url = reverse('movie-collection-list')

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']['collections']) == 1

    def test_update_collection(self):
        collection = CollectionFactory(user=self.user)
        genre = GenreFactory()
        movie = MovieFactory()
        data = {
            "title": "Updated Collection",
            "description": "Updated description",
            "movies": [{"uuid": str(movie.uuid), "title": movie.title, "description": movie.description, "genres": genre.name}]
        }
        url = reverse('movie-collection-detail', kwargs={'pk': collection.uuid})  # Adjust with your actual URL name

        response = self.client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        collection.refresh_from_db()
        assert collection.title == "Updated Collection"

    def test_delete_collection(self):
        collection = CollectionFactory(user=self.user)
        url = reverse('movie-collection-detail', kwargs={'pk': collection.uuid})

        response = self.client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Collection.objects.count() == 0

    def test_retrieve_collection(self):
        collection = CollectionFactory(user=self.user)
        url = reverse('movie-collection-detail', kwargs={'pk': collection.uuid})

        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == collection.title
