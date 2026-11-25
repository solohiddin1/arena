import re
from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from apps.users.models import User


class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        refresh = self.token_class(attrs["refresh"])

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        if not user_id or not User.objects.filter(id=user_id, is_active=True).exists():
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

            data["refresh"] = str(refresh)

        return data


class AuthenticationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=255, required=False)
    username = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        raw_phone = attrs.get("phone_number") or attrs.get("username")
        if not raw_phone:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})

        cleaned = str(raw_phone).strip().replace("+", "").replace(" ", "").replace("-", "")
        attrs["phone_number"] = cleaned
        attrs["username"] = cleaned
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True, max_length=20)
    password = serializers.CharField(required=True, max_length=150, min_length=5)
    full_name = serializers.CharField(required=False, max_length=150, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "phone_number",
            "password",
            "full_name",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def validate_phone_number(self, value):
        cleaned = str(value).strip().replace("+", "").replace(" ", "").replace("-", "")
        phone_regex = r"^998\d{9}$"
        if re.match(phone_regex, cleaned):
            return cleaned
        raise serializers.ValidationError(
            "Phone number must be in the format: '998901234567' or '+998901234567'."
        )


class CheckRegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, max_length=150)
    username = serializers.CharField(required=False, max_length=150)

    def validate(self, attrs):
        raw_phone = attrs.get("phone_number") or attrs.get("username")
        if not raw_phone:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
        cleaned = str(raw_phone).strip().replace("+", "").replace(" ", "").replace("-", "")
        attrs["phone_number"] = cleaned
        attrs["username"] = cleaned
        return attrs


class UserVerifySerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True, allow_null=False)
    code = serializers.CharField(required=True, max_length=4)


class AuthOtpSendSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=20)
    role = serializers.CharField(required=False, max_length=30)

    def validate_phone_number(self, value):
        return str(value).strip().replace("+", "").replace(" ", "").replace("-", "")


class AuthOtpVerifySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    code = serializers.IntegerField(required=True)

