import logging

from django.contrib.auth.hashers import make_password
from django.db import transaction
from dotenv import load_dotenv

from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from accounts_engine.utils import (
    success_true_response,
    success_false_response,
)
from accounts_engine.models import CustomUser, InvalidatedToken
from accounts_engine.serializers import CustomUserSerializer

from accounts_engine.status_code import INTERNAL_SERVER_ERROR

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")
load_dotenv()


class CustomUserViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = CustomUser.objects.filter(is_delete=False, is_admin=False).order_by("-created_datetime")
    serializer_class = CustomUserSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Use a custom serializer that includes nested objects.
        """
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()

        if self.action == "create" or self.action == "update":
            # Use a custom serializer for update actions that includes nested objects
            serializer_class = CustomUserSerializer
        return serializer_class(*args, **kwargs)

    def get_permissions(self):
        if (
            self.request.method == "PATCH"
            or self.request.method == "PUT"
            or self.request.method == "DELETE"
            or self.request.method == "GET"
        ):
            return [IsAuthenticated()]
        else:
            return [AllowAny()]

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            username = request.data.get("username")
            user_queryset = CustomUser.objects.filter(username=username)

            if not user_queryset.exists():
                serializer = self.get_serializer(data=request.data)
                try:
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    instance = serializer.instance
                    instance.password = make_password(instance.password)
                    instance.save()
                    refresh_token = RefreshToken.for_user(instance)

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

            else:
                instance = user_queryset.first()
                refresh_token = RefreshToken.for_user(instance)

            # Create a dictionary containing the relevant data for your response
            response_data = {
                "access_token": str(refresh_token.access_token),
            }

            message = "Congratulation! you successfully login."
            logger_info.info(f"{message} username: {instance.username}")
            return Response(response_data)

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="Internal server error"),
                status=INTERNAL_SERVER_ERROR,
            )


class LogoutAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            auth_header = request.META.get("HTTP_AUTHORIZATION")
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else auth_header
            InvalidatedToken.objects.create(token=token)

            message = "Successfully logout."
            response = Response(success_true_response(message=message))

            logger_info.info(message)
            return response

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="Internal server error"),
                status=INTERNAL_SERVER_ERROR,
            )
