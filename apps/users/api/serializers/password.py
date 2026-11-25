from rest_framework import serializers


class OtpForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, max_length=150)
    username = serializers.CharField(required=False, max_length=150)

    def validate(self, attrs):
        raw_phone = attrs.get("phone_number") or attrs.get("username")
        if not raw_phone:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
        cleaned = str(raw_phone).strip().replace("+", "").replace(" ", "").replace("-", "")
        attrs["phone_number"] = cleaned
        attrs["username"] = cleaned
        return attrs


class VerifyForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, max_length=150)
    username = serializers.CharField(required=False, max_length=150)
    code = serializers.CharField(required=True, max_length=5)

    def validate(self, attrs):
        raw_phone = attrs.get("phone_number") or attrs.get("username")
        if not raw_phone:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
        cleaned = str(raw_phone).strip().replace("+", "").replace(" ", "").replace("-", "")
        attrs["phone_number"] = cleaned
        attrs["username"] = cleaned
        return attrs


class ApplyNewPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, max_length=150)
    username = serializers.CharField(required=False, max_length=150)
    code = serializers.CharField(required=True, max_length=5)
    password = serializers.CharField(required=True, max_length=255)

    def validate(self, attrs):
        raw_phone = attrs.get("phone_number") or attrs.get("username")
        if not raw_phone:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
        cleaned = str(raw_phone).strip().replace("+", "").replace(" ", "").replace("-", "")
        attrs["phone_number"] = cleaned
        attrs["username"] = cleaned
        return attrs

