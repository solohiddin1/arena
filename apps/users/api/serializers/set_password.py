from rest_framework import serializers


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, max_length=150, min_length=4)
