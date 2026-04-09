from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.services.google import GoogleCallback, GoogleLoginRedirect
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

urlpatterns = [

    # register
    path('auth/register/', RegisterUser.as_view(), name='register'),
    path('auth/check-register/', CheckRegister.as_view(), name='check_register'),
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
    
    # google auth
    path('auth/google/login/', GoogleLoginRedirect.as_view(), name='google_login'),
    path('accounts/google/login/callback/', GoogleCallback.as_view(), name='google_callback'),

]
