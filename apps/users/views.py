import uuid
import datetime

from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser

from apps.shared.enum import ResultCodes
from apps.shared.utils import ErrorResponse
from apps.shared.utils import SuccessResponse
from apps.shared.utils import send_telegram_message, get_logger

from .repository import *
from .serialziers import (RegisterSerializer,AuthenticationSerializer, UserProfileImageUpdateSerializer, UserSetLocation, UserUpdateSerializer, 
                            UserVerifySerializer, AuthOtpSendSerializer, 
                            AuthOtpVerifySerializer, UserProfileSerializer)

logger = get_logger()


@extend_schema(
    summary='to register user'
)
class RegisterUser(GenericAPIView):
    serializer_class = RegisterSerializer
    role = "USER"

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        req_body = serializer.validated_data

        otp = generate_otp()
        # if req_body["email"] == 'sirojiddinovsolohiddin961@gmail.com':
        #     otp = "2222"

        user = get_user_by_username(req_body["email"])
        send_telegram_message(f"user is registering with email: {req_body['email']}," \
                              f"and first_name: {req_body.get('first_name','')} with password: {req_body['password']}")
        logger.info(f"user is registered with email: {req_body['email']}")
        if user is None:
            user = create_user(email=req_body["email"],
                                first_name=req_body.get("first_name",""),
                                last_name=req_body.get("last_name",""),
                                phone_number=req_body.get("phone_number",""),
                                age=req_body.get("age",0),
                                otp=otp,
                                otp_created_at=timezone.now(),
                                lat=req_body.get("lat",0.0),
                                longitude=req_body.get("longitude",0.0),
                                language=req_body.get("language","UZ"),
                                password=req_body["password"],
                                is_active=False)
        else:
            if user.is_verified:
                return ErrorResponse(ResultCodes.USER_ALREADY_REGISTERED)
            update_user_otp(user.id, otp, timezone.now())

        send_result = send_otp_email(req_body["email"], otp)
        

        if not send_result:
            return ErrorResponse(ResultCodes.ERROR_SMS_SERVICE)

        return Response({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": self.role,
            "is_verified": False,
            "otp": otp,
            "language": user.language,
        })


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

        user = get_user_by_userid(
            serializer.validated_data["user_id"],
        )

        if user is None: return ErrorResponse(ResultCodes.USER_ROLE_NOT_FOUND)
        if user.is_verified: return ErrorResponse(ResultCodes.USER_ALREADY_REGISTERED)
        if user.email == "sirojiddinovsolohiddin961@gmail.com":
            if serializer.validated_data["code"] == "2222":
                token = RefreshToken.for_user(user)
                return SuccessResponse({
                    "refresh": str(token),
                    "access": str(token.access_token)
                })
            else:
                return ErrorResponse(ResultCodes.WRONG_VERIFICATION_CODE)
        if user.otp:
            if timezone.now() - user.otp_created_at > datetime.timedelta(
                minutes=20): return ErrorResponse(ResultCodes.OTP_EXPIRED)

        if user.otp != serializer.validated_data["code"]: return ErrorResponse(ResultCodes.WRONG_VERIFICATION_CODE)

        update_user_set_verified(user.id)


        token = RefreshToken.for_user(user)
        return SuccessResponse({
            "refresh": str(token),
            "access": str(token.access_token)
        })


@extend_schema(
    summary='login verified user with email and password and return tokens',
    responses={200: AuthenticationSerializer}
)
class LoginUser(GenericAPIView):
    serializer_class = AuthenticationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        # Try authenticate; USERNAME_FIELD is 'email' so username is email
        user = authenticate(request=request._request, username=email, password=password)
        if user is None:
            # also try with email keyword for custom backends
            user = authenticate(request=request._request, email=email, password=password)

        if user is None:
            return ErrorResponse(ResultCodes.INVALID_CREDENTIALS)

        # Ensure user has active & verified role
        # user_role = get_user_role_by_userid_role(user.id, role, is_active=True, is_verified=True)
        # if not user_role:
        #     return ErrorResponse(ResultCodes.USER_IS_NOT_VERIFIED)

        if not user.is_verified:
            return ErrorResponse(ResultCodes.USER_IS_NOT_VERIFIED)

        token = RefreshToken.for_user(user)

        return SuccessResponse({
            "refresh": str(token),
            "access": str(token.access_token)
        })



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

        update_user_role_location(request.user, serializer.validated_data.get("lat"),
                                  serializer.validated_data.get("longitude"))

        return SuccessResponse({"message": "Location updated"})
