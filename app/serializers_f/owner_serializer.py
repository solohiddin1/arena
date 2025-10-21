from rest_framework import serializers
from app.serializers_f.user_serializer import UserSerializer
from app.models.user import User
from app.models.owner import Owner

class OwnerSerializer(serializers.ModelSerializer):   
    class Meta:
        model = Owner
        fields = ['user']
        read_only_fields = ['created_at','updated_at']