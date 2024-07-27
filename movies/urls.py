# urls.py

from django.urls import path, include
from rest_framework import routers
from movies.views import MovieAPIView, MovieCollectionViewSet

router = routers.SimpleRouter()
router.register(r"collection", MovieCollectionViewSet, basename="movie-collection")


urlpatterns = [
    path('movies/', MovieAPIView.as_view(), name='movie-list'),
    path("", include(router.urls)),
]
