from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shared.enum import ResultCodes
from apps.shared.utils import error_response, success_response
from apps.users.api.serializers.poll import TelegramPollSerializer
from apps.users.api.serializers.telegram_otp_verify import TelegramOtpVerifySerializer
from apps.users.services.telegram import TgOtpService


@extend_schema(tags=["auth"], summary="Request Telegram authentication link")
class TelegramOtpView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = None

    def post(self, request, *args, **kwargs):
        try:
            return success_response(TgOtpService.request())
        except Exception as e:
            return error_response(
                ResultCodes.UNKNOWN_ERROR, {"en": str(e), "ru": str(e), "uz": str(e)}
            )


@extend_schema(exclude=True)
class TelegramWebhookView(APIView):
    permission_classes = [AllowAny]
    serializer_class = None

    def post(self, request, *args, **kwargs):
        TgOtpService.handle_update(request.data)
        return Response({"ok": True})


@extend_schema(
    tags=["auth"],
    summary="Poll Telegram authentication status",
    parameters=[TelegramPollSerializer],
)
class TelegramOtpPollView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = TelegramPollSerializer

    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        if not token:
            return error_response(ResultCodes.TOKEN_REQUIRED)
        result = TgOtpService.poll(token)
        if "error" in result:
            err = result["error"]
            if err == "expired":
                return error_response(ResultCodes.LINK_EXPIRED)
            return error_response(ResultCodes.INVALID_REQUEST)
        return success_response(result)


@extend_schema(tags=["auth"], summary="Verify Telegram OTP", request=TelegramOtpVerifySerializer)
class TelegramOtpVerifyView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = TelegramOtpVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get("token")
        otp = serializer.validated_data.get("otp")
        result = TgOtpService.verify_otp(token, otp)
        if "error" in result:
            err = result["error"]
            if err == "expired":
                return error_response(ResultCodes.LINK_EXPIRED)
            return error_response(ResultCodes.INVALID_OTP)
        return success_response(result)
