from django.urls import path
from rest_framework.routers import DefaultRouter

from accounts_engine.views import (
    CustomUserViewSet,
    LogoutAPI,
)

router = DefaultRouter()

router.register("register", CustomUserViewSet, basename="register")

urlpatterns = [
    path("logout/", LogoutAPI.as_view(), name="logout"),
] + router.urls
