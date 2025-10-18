from rest_framework import serializers
from app.models.user import User

class SendEmail(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()  
    # password = serializers.CharField(write_only=True)




























# class StudentRegisterSerializer(serializers.ModelSerializer):
#     # password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ["email", "phone_number"]

#     def create(self, validated_data):
#         return User.objects.create_user(
#             phone_number=validated_data["phone_number"],
#             email=validated_data.get("email"),
#             # password=validated_data["password"],
#         )
    


# class RegisterSerializer(serializers.ModelSerializer):
#     # password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ["email", "phone_number"]

#     def create(self, validated_data):
#         return User.objects.create_user(
#             phone_number=validated_data["phone_number"],
#             email=validated_data.get("email"),
#             # password=validated_data["password"],
#         )