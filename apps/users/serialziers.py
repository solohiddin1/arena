import re
from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from apps.users.models import User, UserDevice,VersionControl
from apps.shared.models import Region , District
# from .repository import 

class AuthenticationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)
    role = serializers.CharField(max_length=255, required=True)


class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        refresh = self.token_class(attrs["refresh"])

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        role = refresh.payload.get("role")

        if not user_id or not role:
            raise AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        # if not exists_user_role_by_userid_role(user_id, role, is_active=True, is_verified=True):
        #     raise AuthenticationFailed(
        #         self.error_messages["no_active_account"],
        #         "no_active_account",
        #     )

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            refresh.outstand()

            data["refresh"] = str(refresh)

        return data
    

class AuthenticationSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True, max_length=150, min_length=5)
    password = serializers.CharField(required=True, max_length=150, min_length=5)
    first_name = serializers.CharField(required=True, max_length=150, min_length=1)
    last_name = serializers.CharField(required=True, max_length=150, min_length=1)
    phone_number = serializers.CharField(required=True, max_length=12, min_length=12)
    age = serializers.IntegerField(required=True)
    lat = serializers.FloatField(required=False)
    long = serializers.FloatField(required=False)
    lang = serializers.CharField(required=False, max_length=2, min_length=2, default="UZ")
    # region = serializers.IntegerField(
    #     required=False, allow_null=False,
    #     help_text="Region ID"
    #     )
    # district = serializers.IntegerField(
    #     required=False, allow_null=False,
    #     help_text="District ID"
    #     )

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "age",
            "lat",
            "long",
            "lang",
            "region",
            "district",
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_phone_number(self, value):
        phone_regex = r'^998\d{9}$'  # Uzbek phone: 998 + 9 digits
        if re.match(phone_regex, value):
            return value
        raise serializers.ValidationError(
            "Phone number must be in the format: '998901234567'."
        )
    
    def validate_email(self, value):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        phone_regex = r'^998\d{9}$'  # Uzbek phone: 998 + 9 digits

        if re.match(email_regex, value) or re.match(phone_regex, value):
            return value

        raise serializers.ValidationError(
            "Username must be a valid email or Uzbek phone number (e.g. 998901234567)."
        )



class UserVerifySerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True, allow_null=False)
    code = serializers.CharField(required=True, max_length=4)



class AuthOtpSendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=150)
    role = serializers.CharField(required=True, max_length=30)



class AuthOtpVerifySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    code = serializers.IntegerField(required=True,)



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # allow user to update their profile fields but not change email or permissions here
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "image",
            "age",
            "lat",
            "longitude",
            "language",
            "region",
            "district",
            "is_active",
            "is_verified",
        )
        read_only_fields = ("id", "email")

    def update(self, instance, validated_data):
        # Use set_password elsewhere; do not allow password change here
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserProfileImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["image"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'language']

class UserSetLocation(serializers.Serializer):
    lat = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)


class OtpForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=150)


class VerifyForgotPasswordSerializer(serializers.Serializer):
    reset_id = serializers.IntegerField(required=True)
    code = serializers.CharField(required=True, max_length=5)


class ApplyNewPasswordSerializer(serializers.Serializer):
    reset_token = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=255)
