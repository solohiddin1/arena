from django.urls import path
# # from apps.app.views.admin import TeacherCrud, admin_panel, teacher_panel
# from apps.users.views import (ChangePasswordView, LogoutApiView , ForgotPasswordView,
#     home, reset_page, reset_password, student_dashboard, UserLoginView, userlogin_view, loginexistinguser,
#     loginexistinguser_view, verify_user_email_view,
#     verify, LoginApiView, VerifyOtpView, )

# from apps.users.views import UserRegisterView , DeleteUser, GetAllUsers

# from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
# from apps.users.views import ArenaCreateView, ArenaListView
# from apps.users.views import OwnerProfileView, OwnerRegisterView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (LoginUser, UserProfileView, UserUpdate, 
                    UserUpdateProfileImage, UserUpdateProfileImage, 
                    VerifyOtp, RegisterUser, UserLocationUpdate,
                    ApplyNewPassword, OtpForgotPassword, VerifyForgotPassword)

urlpatterns = [
    # path('auth/token/',TokenObtainPairView.as_view(), name='token'),
    # path('auth/token/refresh/',TokenRefreshView.as_view(), name='token_refresh'),

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

]

#     # owner
#     path('owner_register/',OwnerRegisterView.as_view(),name='register_owner'),
#     path('get_owner/',OwnerProfileView.as_view(),name='get_owner'),

#     # users
#     path('get_users/',GetAllUsers.as_view(),name='get_users'),

#     # login
#     path('userlogin/',UserLoginView.as_view(),name='userlogin'),
#     path('userlogin/view/',userlogin_view,name='userlogin_view'),

#     path('login_existing_user/',loginexistinguser,name='login_existing_user'),
#     # path('login_existing_user/view',loginexistinguser_view,name='login_existing_user_view'),


#     # # log out
#     path('logout/',LogoutApiView.as_view(),name='logout'),

#     # change password
#     # path('change_password_page/',change_password_page,name='change_password_page'),
#     path('change_password/',ChangePasswordView.as_view(),name='change_password'),
    
#     # forgot password
#     path('forgot_password/',ForgotPasswordView.as_view(),name='forgot_password'),    
#     path('reset-password/<uidb64>/<token>/',reset_password, name='reset_password'),
#     # path('reset-password/<uiid64>/<token>/',reset_page, name='reset_page'),

#     # user registration 
#     path('user_register/',UserRegisterView.as_view(),name='user_register'),
#     path('delete_user/<int:pk>/',DeleteUser.as_view(), name="delete"),

#     # auth
#     path('verify_otp/',VerifyOtpView.as_view(),name='verify_user_otp'),

    
#     # token
#     path('token/',TokenObtainPairView.as_view()),
#     path('token/refresh/',TokenRefreshView.as_view()),

#     # path('',home, name='home'),

# ]`