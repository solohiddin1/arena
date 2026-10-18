from rest_framework import serializers

class TelegramPollSerializer(serializers.Serializer):
    token = serializers.CharField()
