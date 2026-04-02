from drf_spectacular.utils import extend_schema
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from apps.shared.enum import ResultCodes
from apps.shared.utils import ErrorResponse, SuccessResponse
from apps.shared.utils import SuccessResponse
from apps.shared.utils import send_telegram_message, get_logger
from .repository import *
from .services.user_service import UserService
from .serialziers import (ApplyNewPasswordSerializer, OtpForgotPasswordSerializer,\
                           RegisterSerializer,AuthenticationSerializer, UserProfileImageUpdateSerializer,\
                              UserSetLocation, UserUpdateSerializer, 
                            UserVerifySerializer, AuthOtpSendSerializer, 
                            AuthOtpVerifySerializer, UserProfileSerializer, VerifyForgotPasswordSerializer)

logger = get_logger()
user_service = UserService()
ACCEPT_LANGUAGE_HEADER = []


@extend_schema(
    parameters=ACCEPT_LANGUAGE_HEADER,
    summary='to register user'
)
class RegisterUser(GenericAPIView):
    serializer_class = RegisterSerializer
    filter_backends=[DjangoFilterBackend]
    role = "USER"

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.register_user(serializer.validated_data)
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])


@extend_schema(
    summary='to verify registered user, send users id and otp , user id is ' \
    'when returned when they are  registered'
)
class VerifyOtp(GenericAPIView):
    serializer_class = UserVerifySerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.verify_registration_otp(
            user_id=serializer.validated_data["user_id"],
            code=serializer.validated_data["code"],
        )
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])


@extend_schema(
    summary='login verified user with email and password and return tokens',
    responses={200: AuthenticationSerializer}
)
class LoginUser(GenericAPIView):
    serializer_class = AuthenticationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.login_user(
            request=request,
            email=serializer.validated_data.get("email"),
            password=serializer.validated_data.get("password"),
        )
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])


@extend_schema(
    summary='Get authenticated user profile'
)
class UserProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return SuccessResponse(UserProfileSerializer(request.user, context={'request': request}).data)


class UserUpdateProfileImage(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileImageUpdateSerializer
    parser_classes = [MultiPartParser]
    http_method_names = ['patch']

    def get_object(self):
        return self.request.user

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {'type': 'string', 'format': 'binary'}
                }
            }
        }
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfileImageUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return SuccessResponse({"message": "Image updated"})

        return ErrorResponse(ResultCodes.UNKNOWN_ERROR)


class UserUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer
    http_method_names = ['patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return SuccessResponse(serializer.data)


class UserLocationUpdate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSetLocation
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.update_user_location(
            user=request.user,
            lat=serializer.validated_data.get("lat"),
            longitude=serializer.validated_data.get("longitude"),
        )
        return SuccessResponse(result["data"])


class OtpForgotPassword(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = OtpForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.request_forgot_password_otp(serializer.validated_data["email"])
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])


class VerifyForgotPassword(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = VerifyForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.verify_forgot_password(
            reset_id=serializer.validated_data['reset_id'],
            code=serializer.validated_data['code'],
        )
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])


class ApplyNewPassword(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ApplyNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = user_service.apply_new_password(
            reset_token=serializer.validated_data['reset_token'],
            password=serializer.validated_data['password'],
        )
        if result.get("error"):
            return ErrorResponse(result["error"])
        return SuccessResponse(result["data"])
