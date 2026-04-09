import requests
from rest_framework import status
from apps.shared.utils import SuccessResponse, ErrorResponse
from apps.users.models import User
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from apps.shared.enum import ResultCodes
from django.conf import settings

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
        return redirect(google_url)
    

@extend_schema(tags=["google"], summary="Handles Google OAuth callback")
class GoogleCallback(APIView):
    """
    Handles Google OAuth callback, registers/logs in the user
    """
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return ErrorResponse(ResultCodes.NO_CODE_PROVIDED)

        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        r = requests.post(token_url, data=data)
        token_response = r.json()
        id_token = token_response.get("id_token")
        access_token = token_response.get("access_token")

        if not id_token:
            return ErrorResponse(ResultCodes.FAILED_TO_OBTAIN_TOKEN)

        # Get user info from Google
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(userinfo_url, headers=headers)
        user_info = r.json()

        # Create or get user
        email = user_info.get("email")
        user, created = User.objects.get_or_create(email=email, defaults={
            "full_name": user_info.get("given_name", ""),
            "username": email,
            "is_active": True,
        }) 

        user.is_verified = True
        user.is_from_social = True
        if not user.has_usable_password():
            user.set_unusable_password()
        user.save()

        # Here you can generate token (JWT or DRF token)
        # Example using DRF Token:
        from rest_framework.authtoken.models import Token
        from urllib.parse import quote
        # token, _ = Token.objects.get_or_create(user=user)
        token = RefreshToken.for_user(user)

        # Redirect to frontend callback with tokens
        # Encode tokens to handle special characters
        access_token = str(token.access_token)
        refresh_token = str(token)
        
        is_mobile = request.query_params.get("mobile") == "1"
        if is_mobile:
            redirect_url = f"myapp://auth/callback?access={quote(access_token)}&refresh={quote(refresh_token)}"
        else:
            redirect_url = f"{settings.FRONTEND_URL}/auth/callback?access={quote(access_token)}&refresh={quote(refresh_token)}"
        return redirect(redirect_url)

        # return redirect(redirect_url)

