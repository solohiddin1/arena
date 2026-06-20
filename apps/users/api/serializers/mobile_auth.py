from rest_framework import serializers

class GoogleMobileAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()