from django.urls import path
from app.views.admin import TeacherCrud, admin_panel, teacher_panel
# from app.views.mock_data import MockDataActiveStudents, MockDataFinished, MockDataView, MockTwoCount
from app.views.auth import (ChangePasswordView, LogoutApiView , ForgotPasswordView,
    home, reset_page, reset_password, student_dashboard, userlogin, userlogin_view, loginexistinguser,
    loginexistinguser_view, verify_user_email_view,
    verify, login, VerifyOtpView, )

from app.views.user import UserRegisterView , DeleteUser

from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
# from app.views.mock_data import MockTwoMonth

urlpatterns = [
    # mock data
    # path('mock_data/<int:year>/<int:month>/',MockDataView.as_view(),name='mock_data'),
    # path('mock_2/<str:date1>/<str:date2>/',MockTwoMonth.as_view(),name='mock_data_two_months'),

    # path('mock_data/active_students/',MockDataActiveStudents.as_view(),name='mock_data_active_students'),
    # path('mock_2_count/<str:date1>/<str:date2>/',MockTwoCount.as_view(),name='mock_data_two_months'),
    # path('mock_2_finished/',MockDataFinished.as_view(),name='mock_data_two_months_finished'),

    
    # login
    path('userlogin/',userlogin,name='userlogin'),
    path('userlogin/view/',userlogin_view,name='userlogin_view'),

    path('login_existing_user/',loginexistinguser,name='login_existing_user'),
    # path('login_existing_user/view',loginexistinguser_view,name='login_existing_user_view'),


    # # log out0
    path('logout/',LogoutApiView.as_view(),name='logout'),


    # change password
    # path('change_password_page/',change_password_page,name='change_password_page'),
    path('change_password/',ChangePasswordView.as_view(),name='change_password'),
    
    # forgot password
    path('forgot_password/',ForgotPasswordView.as_view(),name='forgot_password'),
    
    path('reset-password/<uidb64>/<token>/',reset_password, name='reset_password'),

    # path('reset-password/<uiid64>/<token>/',reset_page, name='reset_page'),


    # auth
    path('verify_otp/',VerifyOtpView.as_view(),name='verify_user_otp'),

    path('user_register/',UserRegisterView.as_view(),name='user_register'),

    path('delete_user/<int:pk>/',DeleteUser.as_view(), name="delete"),
    
    # token
    path('token/',TokenObtainPairView.as_view()),
    path('token/refresh/',TokenRefreshView.as_view()),

    # path('',home, name='home'),

]