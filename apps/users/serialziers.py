from typing import Any
from rest_framework import serializers
import re
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from apps.users.models import User, UserRole, UserDevice,VersionControl
from .repository import exists_user_role_by_userid_role

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

        if not exists_user_role_by_userid_role(user_id, role, is_active=True, is_verified=True):
            raise AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

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
    

class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=150, min_length=5)
    password = serializers.CharField(required=True, max_length=150, min_length=5)
    first_name = serializers.CharField(required=False, max_length=150, min_length=1)
    lat = serializers.FloatField(required=False)
    long = serializers.FloatField(required=False)
    lang = serializers.CharField(required=False, max_length=2, min_length=2, default="UZ")

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
    role = serializers.CharField(required=True, max_length=30)
    code = serializers.CharField(required=True, max_length=4)
