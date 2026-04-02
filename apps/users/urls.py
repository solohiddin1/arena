from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.services.google import GoogleCallback, GoogleLoginRedirect
from .views import (LoginUser, UserProfileView, UserUpdate, 
                    UserUpdateProfileImage, UserUpdateProfileImage, 
                    VerifyOtp, RegisterUser, UserLocationUpdate,
                    ApplyNewPassword, OtpForgotPassword, VerifyForgotPassword)

urlpatterns = [

    # register
    path('auth/register/', RegisterUser.as_view(), name='register'),
    path('auth/verify-otp/', VerifyOtp.as_view(), name='verify_otp'),

    # login
    path('auth/login/', LoginUser.as_view(), name='login'),

    path('get-profile/', UserProfileView.as_view(), name='get_profile'),
    path('profile-image-update/', UserUpdateProfileImage.as_view(), name='profile_image_update'),
    path('profile-update/', UserUpdate.as_view(), name='profile_update'),

    # password
    path("otp-forgot-password/", OtpForgotPassword.as_view(), name="otp_forgot_password"),
    path("verify-forgot-password/", VerifyForgotPassword.as_view(), name="verify_forgot_password"),
    path("password-reset/", ApplyNewPassword.as_view(), name="password_reset"),


    path('profile-location-update/', UserLocationUpdate.as_view(), name='profile_location_update'),


    # google auth
    path('auth/google/login/', GoogleLoginRedirect.as_view(), name='google_login'),
    path('accounts/google/login/callback/', GoogleCallback.as_view(), name='google_callback'),

]
