from rest_framework import serializers

from apps.users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "image",
            "age",
            "is_active",
            "is_verified",
        )
        read_only_fields = ("id", "email")

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserProfileImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["image"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number"]
