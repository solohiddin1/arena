from rest_framework import serializers
from app.models.category import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = 'name'
        read_only_fields = ['created_at','updated_at']