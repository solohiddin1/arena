from rest_framework import serializers


class OtpForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=150)


class VerifyForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=150)
    code = serializers.CharField(required=True, max_length=5)


class ApplyNewPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=150)
    code = serializers.CharField(required=True, max_length=5)
    password = serializers.CharField(required=True, max_length=255)
