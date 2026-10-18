from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.services.google import GoogleCallback, GoogleLoginRedirect, GoogleMobileAuth
from apps.users.api.views.apply_new_password import ApplyNewPassword
from apps.users.api.views.check_register import CheckRegister
from apps.users.api.views.login_user import LoginUser
from apps.users.api.views.otp_forgot_password import OtpForgotPassword
from apps.users.api.views.profile_view import UserProfileView
from apps.users.api.views.register import RegisterUser
from apps.users.api.views.user_update import UserUpdate
from apps.users.api.views.update_profile_image import UserUpdateProfileImage
from apps.users.api.views.verify_forgot_password import VerifyForgotPassword
from apps.users.api.views.verify_otp import VerifyOtp

from apps.users.api.views.device_add import DeviceAddView
from apps.users.api.views.device_delete import DeviceDeleteView
from apps.users.api.views.telegram_otp import (
    TelegramOtpPollView,
    TelegramOtpVerifyView,
    TelegramOtpView,
    TelegramWebhookView,
)

urlpatterns = [

    # register
    path('auth/register/', RegisterUser.as_view(), name='register'),
    path('auth/check-register/', CheckRegister.as_view(), name='check_register'),
    path('auth/verify-otp/', VerifyOtp.as_view(), name='verify_otp'),

    # login
    path('auth/login/', LoginUser.as_view(), name='login'),

    # telegram auth
    path('auth/telegram/request/', TelegramOtpView.as_view(), name='telegram_otp_request'),
    path('auth/telegram/webhook/', TelegramWebhookView.as_view(), name='telegram_webhook'),
    path('auth/telegram/poll/', TelegramOtpPollView.as_view(), name='telegram_otp_poll'),
    path('auth/telegram/verify/', TelegramOtpVerifyView.as_view(), name='telegram_otp_verify'),

    # devices
    path('devices/add/', DeviceAddView.as_view(), name='device_add'),
    path('devices/<int:device_id>/delete/', DeviceDeleteView.as_view(), name='device_delete'),
    path('devices/<str:device_id>/delete/', DeviceDeleteView.as_view(), name='device_delete_str'),

    path('get-profile/', UserProfileView.as_view(), name='get_profile'),
    path('profile-image-update/', UserUpdateProfileImage.as_view(), name='profile_image_update'),
    path('profile-update/', UserUpdate.as_view(), name='profile_update'),

    # password
    path("otp-forgot-password/", OtpForgotPassword.as_view(), name="otp_forgot_password"),
    path("verify-forgot-password/", VerifyForgotPassword.as_view(), name="verify_forgot_password"),
    path("password-reset/", ApplyNewPassword.as_view(), name="password_reset"),
    
    # google auth
    path('auth/google/login/', GoogleMobileAuth.as_view(), name='google_login'),
    path('accounts/google/login/callback/', GoogleCallback.as_view(), name='google_callback'),
    # path('auth/google/mobile/', GoogleMobileAuth.as_view(), name='google_mobile_auth'),

]
