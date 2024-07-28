# urls.py

from django.urls import path, include
from rest_framework import routers
from movies.views import MovieAPIView, MovieCollectionViewSet, RequestCountView, ResetRequestCountView

router = routers.SimpleRouter()
router.register(r"collection", MovieCollectionViewSet, basename="movie-collection")


urlpatterns = [
    path("movies/", MovieAPIView.as_view(), name="movie-list"),
    path("request-count/", RequestCountView.as_view(), name="request-count"),
    path("request-count/reset/", ResetRequestCountView.as_view(), name="request-count-reset"),
    path("", include(router.urls)),
]
