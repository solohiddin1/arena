from rest_framework import serializers
from app.models import Arena

class ArenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arena
        fields = ['name', 'location', 'image', 'owner', 'cost', 'open_time', 'close_time']
        read_only_fields = ['id','created_at', 'updated_at']