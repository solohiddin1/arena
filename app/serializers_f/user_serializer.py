from rest_framework import serializers
from app.models import User
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','phone_number']
        read_only_fields = ['is_teacher','is_admin','is_student','created_at','updated_at']

    def create(self, validated_data):
        validated_data['is_teacher'] = False
        validated_data['is_admin'] = False
        validated_data['is_student'] = False
        return super().create_user(**validated_data)

    def email_verification(self, user):
        email = getattr(user, "email", None)
        if not email:
            return False
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "phone_number", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            phone_number=validated_data["phone_number"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
    

class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)