import logging

from django.contrib.auth.hashers import make_password
from django.db import transaction
from dotenv import load_dotenv

from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from accounts_engine.utils import (
    success_true_response,
    success_false_response,
    check_otp,
)
from accounts_engine.models import CustomUser, InvalidatedToken
from accounts_engine.serializers import CustomUserSerializer, VerifyAccountSerializer

from accounts_engine.sms import send_otp
from accounts_engine.status_code import BAD_REQUEST, INTERNAL_SERVER_ERROR

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
            contact = request.data.get("contact")
            user_queryset = CustomUser.objects.filter(contact=contact)
            if not user_queryset.exists():
                request.data["password"] = "Dedust!23"
                serializer = self.get_serializer(data=request.data)
                try:
                    serializer.is_valid(raise_exception=True)
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

                self.perform_create(serializer)
                instance = serializer.instance

                # Perform modifications before accessing serializer.data
                domain = request.get_host()
                sms_details = send_otp(instance.contact, domain)
                if sms_details["success"]:
                    instance.otp = sms_details["otp"]
                    instance.otp_send_datetime = timezone.now()
                    instance.password = make_password(instance.password)
                    instance.save()

                    message = "Successfully signup verification otp send"
                    logger_info.info(f"{message} Phone number: {instance.contact}")
                    headers = self.get_success_headers(serializer.data)
                    return Response(success_true_response(message=message), headers=headers)

                else:
                    instance.delete()
                    message = "Invalid phone number entered"
                    logger_error.error(message)
                    return Response(success_false_response(message=message), status=BAD_REQUEST)

            user = user_queryset.first()

            domain = request.get_host()
            sms_details = send_otp(user.contact, domain)
            user.otp = sms_details["otp"]
            user.otp_send_datetime = timezone.now()
            user.save()
            message = "Successfully login verification otp send"
            logger_info.info(f"{message} Phone number: {user.contact}")
            return Response(success_true_response(message=message))

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="Internal server error"),
                status=INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["PUT", "PATCH"])
    def update_user(self, request, *args, **kwargs):

        try:
            partial = kwargs.pop("partial", True)
            instance = request.user
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                error_detail = e.detail
                for field_name, errors in error_detail.items():
                    for error in errors:
                        message = str(error)
                        logger_error.error(message)
                        return Response(success_false_response(message=message))

            self.perform_update(serializer)

            return Response(success_true_response(message="Profile updated successfully"))

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="Internal server error"),
                status=INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["GET"])
    def get_user_profile(self, request, *args, **kwargs):

        try:
            instance = request.user
            serializer = self.get_serializer(instance)
            data = serializer.data

            message = "Successfully fetched profile data."
            logger_info.info(f"Successfully fetched user: {instance.username}, profile data.")
            return Response(success_true_response(data=data, message=message))

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="Internal server error"),
                status=INTERNAL_SERVER_ERROR,
            )


class VerifyOTPViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = VerifyAccountSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            contact = data["contact"]
            input_otp = data["otp"]
            user_queryset = CustomUser.objects.filter(contact=contact)

            if not user_queryset:
                message = "Sorry, the phone number is not linked to an account. " "Please verify and try again."
                logger_info.info(message)
                return Response(success_false_response(message=message), status=BAD_REQUEST)

            user = user_queryset.first()

            check_otp_details = check_otp(user, input_otp)

            if check_otp_details["is_verification_failed"]:
                message = check_otp_details["message"]
                logger_info.info(message)
                return Response(success_false_response(message=message), status=BAD_REQUEST)

            if not user.is_active:
                user.is_active = True
                user.save()
                logger_info.info("Successfully account activated.")

            refresh_token = RefreshToken.for_user(user)

            # Create a dictionary containing the relevant data for your response
            response_data = {
                "access_token": str(refresh_token.access_token),
            }

            message = "Login successful"
            logger_info.info(message)

            return Response(success_true_response(data=response_data, message=message))

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


class SendOtpAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            domain = request.get_host()
            sms_details = send_otp(user.contact, domain)
            user.otp = sms_details["otp"]
            user.otp_send_datetime = timezone.now()
            user.save()
            message = "Successfully otp send to your registered number}"
            logger_info.info(f"{message} Phone number: {user.contact}")
            return Response(success_true_response(message=message))

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="Internal server error"),
                status=INTERNAL_SERVER_ERROR,
            )
