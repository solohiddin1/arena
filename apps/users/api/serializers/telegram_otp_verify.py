from rest_framework import serializers


class TelegramOtpVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128)
    otp = serializers.CharField(max_length=8)
