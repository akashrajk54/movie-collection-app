# views.py
from django.db import transaction
from rest_framework import status
import logging
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from dotenv import load_dotenv
from django.db.models import Count
from rest_framework.viewsets import ModelViewSet

from .serializers import CollectionSerializer
from movies.models import MovieCollection, MovieGenre, Collection
from movies.movie_service import MovieService, MovieCollectionService, CollectionUpdateService
from rest_framework.response import Response
from accounts_engine.utils import (
    success_false_response,
)

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")
load_dotenv()


class MovieAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        page_number = request.query_params.get("page", 1)
        movie_service = MovieService()

        try:
            movies_data = movie_service.fetch_movies(page=int(page_number))
            logger_info.info(f"Fetched movies for page {page_number}")

            return Response(movies_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger_error.error(f"Error fetching movies: {str(e)}")
            return Response(
                success_false_response(message="An unexpected error occurred. Please try again later."),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MovieCollectionViewSet(ModelViewSet):
    queryset = MovieCollection.objects.all()
    serializer_class = CollectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.MovieCollectionService = None

    def initialize_service(self, user, collection):
        # Initialize the service with the necessary context
        self.MovieCollectionService = MovieCollectionService(user, collection)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            data = request.data.copy()
            data["user"] = user.id
            # collection_data = {
            #     'title': data.get('title'),
            #     'description': data.get('description'),
            #     'user': user.id
            # }

            # Create the collection
            collection_serializer = CollectionSerializer(data=data, context={"request": request})
            collection_serializer.is_valid(raise_exception=True)
            collection = collection_serializer.save()

            # Initialize the movie service and process movies data
            self.initialize_service(user, collection)
            self.MovieCollectionService.save_movies_and_link_genres(data.get("movies", []))

            collection_uuid = collection_serializer.data.get("uuid")
            return Response({"collection_uuid": collection_uuid}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            error_detail = e.detail
            for field_name, errors in error_detail.items():
                for error in errors:
                    message = str(error)
                    logger_error.error(message)
                    message = {"message": message}
                    return Response(
                        message,
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="An unexpected error occurred. Please try again later."),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            user = request.user

            # Get collections for the user
            collections = Collection.objects.filter(user=user)
            collection_serializer = CollectionSerializer(
                collections, many=True, context={"request": request, "view": self}
            )

            # Get favorite genres
            favorite_genres = (
                MovieGenre.objects.filter(movie__movie_collections__user=user)
                .values("genre__name")
                .annotate(genre_count=Count("genre"))
                .order_by("-genre_count")[:3]
            )

            favorite_genres_list = [genre["genre__name"] for genre in favorite_genres]
            favorite_genres_str = ", ".join(favorite_genres_list)

            return Response(
                {
                    "is_success": True,
                    "data": {"collections": collection_serializer.data, "favourite_genres": favorite_genres_str},
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="An unexpected error occurred. Please try again later."),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            collection_uuid = kwargs.get("pk")
            data = request.data
            CollectionUpdateService.update_collection_and_movies(request.user, collection_uuid, data)

            return Response({"collection_uuid": collection_uuid}, status=status.HTTP_200_OK)

        except Collection.DoesNotExist:
            return Response({"success": False, "message": "Collection not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger_error.error(str(e))
            return Response(
                {"success": False, "message": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            collection_uuid = kwargs.get("pk")
            collection = Collection.objects.get(uuid=collection_uuid, user=request.user)
            serializer = CollectionSerializer(collection, context={"request": request, "view": self})
            return Response(serializer.data)
        except Collection.DoesNotExist:
            message = "Collection not found."
            logger_error.error(message)
            return Response({"success": False, "message": message}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger_error.error(str(e))
            message = "An unexpected error occurred. Please try again later."
            return Response(
                {"success": False, "message": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            collection_uuid = kwargs.get("pk")
            collection = Collection.objects.get(uuid=collection_uuid, user=request.user)

            # Delete the collection
            collection.delete()

            return Response(
                {"success": True, "message": "Collection deleted successfully."}, status=status.HTTP_204_NO_CONTENT
            )

        except Collection.DoesNotExist:
            return Response({"success": False, "message": "Collection not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger_error.error(str(e))
            return Response(
                {"success": False, "message": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RequestCountView(APIView):

    def get(self, request, *args, **kwargs):
        request_count = cache.get("request_count", 0)
        return Response({"requests": request_count}, status=status.HTTP_200_OK)


class ResetRequestCountView(APIView):

    def post(self, request, *args, **kwargs):
        cache.set("request_count", 0)
        return Response({"message": "request count reset successfully"}, status=status.HTTP_201_CREATED)
