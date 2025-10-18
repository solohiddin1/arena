from rest_framework import serializers
from app.models import Arena

class ArenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arena
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']