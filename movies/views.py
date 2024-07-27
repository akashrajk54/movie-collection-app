# views.py

import logging

from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from dotenv import load_dotenv

from rest_framework.viewsets import ModelViewSet

from accounts_engine import status_code
from .models import MovieCollection
from .serializers import MovieCollectionSerializer

from accounts_engine.status_code import INTERNAL_SERVER_ERROR
from .movie_service import MovieService
from rest_framework.response import Response
from accounts_engine.utils import (
    success_true_response,
    success_false_response,
)

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")
load_dotenv()


class MovieAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        page_number = request.query_params.get('page', 1)
        movie_service = MovieService()

        try:
            movies_data = movie_service.fetch_movies(page=int(page_number))
            logger_info.info(f"Fetched movies for page {page_number}")

            message = "Successfully fetched movies data."
            return Response(success_true_response(data=movies_data, message=message))
        except Exception as e:
            logger_error.error(f"Error fetching movies: {str(e)}")
            return Response(
                success_false_response(message="Internal server error"),
                status=INTERNAL_SERVER_ERROR,
            )


class MovieCollectionViewSet(ModelViewSet):
    queryset = MovieCollection.objects.all()
    serializer_class = MovieCollectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            requested_data = request.data.copy()
            requested_data["user"] = user.id
            serializer = self.get_serializer(data=requested_data)

            try:
                serializer.is_valid(raise_exception=True)

                self.perform_create(serializer)
                instance = serializer.instance
                message = "Successfully movie added to collection."
                logger_info.info(f"{message} by {user.username}")
                return Response(
                    success_true_response(data={"uuid": instance.uuid}, message=message),
                    status=status_code.CREATED,
                )

            except ValidationError as e:
                error_detail = e.detail
                for field_name, errors in error_detail.items():
                    for error in errors:
                        message = str(error)
                        logger_error.error(message)
                        return Response(
                            success_false_response(message=message),
                            status=e.status_code,
                        )

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="An unexpected error occurred. Please try again later."),
                status=status_code.INTERNAL_SERVER_ERROR,
            )



