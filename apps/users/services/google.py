import jwt
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.generics import GenericAPIView

from apps.shared.middleware.middleware import get_logger
from apps.shared.utils import SuccessResponse, ErrorResponse
from apps.users.api.serializers.mobile_auth import GoogleMobileAuthSerializer
from apps.users.models import User
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from apps.shared.enum import ResultCodes
from django.conf import settings

logger = get_logger()

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

@extend_schema(tags=["google"], summary="Redirects user to Google for authentication")
class GoogleLoginRedirect(APIView):
    def get(self, request):
        google_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            "?response_type=code"
            f"&client_id={GOOGLE_CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            "&scope=openid%20email%20profile"
            "&access_type=offline"
        )
        return SuccessResponse(result=google_url)
    

@extend_schema(tags=["google"], summary="Handles Google OAuth callback")
class GoogleCallback(APIView):
    """
    Handles Google OAuth callback, registers/logs in the user
    """
    def get(self, request):
        from urllib.parse import quote
        code = request.query_params.get("code")
        if not code:
            logger.warning("GoogleCallback | no authorization code in request")
            return ErrorResponse(ResultCodes.NO_CODE_PROVIDED)

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        logger.info("GoogleCallback | exchanging code for tokens")
        r = requests.post(token_url, data=data)
        token_response = r.json()
        id_token = token_response.get("id_token")
        access_token = token_response.get("access_token")

        if not id_token:
            logger.error(f"GoogleCallback | failed to obtain id_token | Google response: {r.status_code} {token_response.get('error')}")
            return ErrorResponse(ResultCodes.FAILED_TO_OBTAIN_TOKEN)

        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        logger.info("GoogleCallback | fetching userinfo from Google")
        r = requests.get(userinfo_url, headers=headers)
        user_info = r.json()

        email = user_info.get("email")
        logger.info(f"GoogleCallback | got userinfo | email={email}")

        user, created = User.objects.get_or_create(email=email, defaults={
            "full_name": user_info.get("given_name", ""),
            "username": email,
            "is_active": True,
        })
        logger.info(f"GoogleCallback | user {'created' if created else 'found'} | email={email}")

        user.is_verified = True
        user.is_from_social = True
        if not user.has_usable_password():
            user.set_unusable_password()
        user.save()

        token = RefreshToken.for_user(user)
        access_token = str(token.access_token)
        refresh_token = str(token)

        is_mobile = request.query_params.get("mobile") == "1"
        if is_mobile:
            redirect_url = f"myapp://auth/callback?access={quote(access_token)}&refresh={quote(refresh_token)}"
        else:
            redirect_url = f"{settings.FRONTEND_URL}/auth/callback?access={quote(access_token)}&refresh={quote(refresh_token)}"

        logger.info(f"GoogleCallback | redirecting | mobile={is_mobile} | email={email}")
        return redirect(redirect_url)


@extend_schema(tags=["google"],
               summary="Mobile Google auth - exchange Google id_token for JWT")
class GoogleMobileAuth(GenericAPIView):
    serializer_class = GoogleMobileAuthSerializer
    def post(self, request):
        id_token_str = request.data.get("id_token")
        if not id_token_str:
            logger.warning("GoogleMobileAuth | no id_token in request")
            return ErrorResponse(ResultCodes.NO_CODE_PROVIDED)
        decoded = jwt.decode(id_token_str, options={"verify_signature": False})
        print(decoded)
        logger.info("GoogleMobileAuth | verifying id_token with google-auth library")
        try:
            user_info = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                GOOGLE_CLIENT_ID,
            )
        except ValueError as e:
            error_msg = str(e)
            if "Token expired" in error_msg:
                logger.error(f"GoogleMobileAuth | token expired | {e}")
            else:
                logger.error(f"GoogleMobileAuth | token verification failed | {e}")
            return ErrorResponse(ResultCodes.FAILED_TO_OBTAIN_TOKEN)

        email = user_info.get("email")
        logger.info(f"GoogleMobileAuth | token valid | email={email}")

        user, created = User.objects.get_or_create(email=email, defaults={
            "full_name": user_info.get("given_name", ""),
            "username": email,
            "is_active": True,
        })
        logger.info(f"GoogleMobileAuth | user {'created' if created else 'found'} | email={email}")

        user.is_verified = True
        user.is_from_social = True
        if not user.has_usable_password():
            user.set_unusable_password()
        user.save()

        token = RefreshToken.for_user(user)
        logger.info(f"GoogleMobileAuth | JWT issued | email={email}")
        return SuccessResponse(result={
            "access": str(token.access_token),
            "refresh": str(token),
        })

