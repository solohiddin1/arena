from django.urls import path
from app.views.admin import TeacherCrud, admin_panel, teacher_panel
# from app.views.mock_data import MockDataActiveStudents, MockDataFinished, MockDataView, MockTwoCount
from app.views.auth import (forgot_password_view, logout_view , forgot_password, 
    home, reset_page, reset_password, student_dashboard, userlogin, userlogin_view, loginexistinguser,
    loginexistinguser_view, verify_user_email_view,
    verify, login, verify_user_email, change_password, )
# from app.views.owner import TeacherCreateView, TeacherProfileView
# from app.views.user import (register, 
    #  delete_user)
from app.views.user import UserRegisterView

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
    path('api/logout/',logout_view,name='logout'),


    # change password
    # path('change_password_page/',change_password_page,name='change_password_page'),
    path('api/change_password/',change_password,name='change_password'),
    
    # forgot password
    path('forgot_password/',forgot_password,name='forgot_password'),
    path('forgot_password/view/',forgot_password_view,name='forgot_password_view'),
    
    path('reset-password/<uidb64>/<token>/',reset_password, name='reset_password'),
    path('api/reset-password/<uiid64>/<token>/',reset_page, name='reset_page'),


    # auth
    path('verify_user_otp/',verify_user_email,name='verify_user_otp'),
    # path('verify_user_otp/view',verify_user_email_view,name='verify_user_otp_view'),

    path('user_register/',UserRegisterView.as_view(),name='user_register'),

    # path('delete_user/<int:pk>/',delete_user, name="delete"),
    
    # token
    path('api/token/',TokenObtainPairView.as_view()),
    path('api/token/refresh/',TokenRefreshView.as_view()),

    path('',home, name='home'),

    # path('register/', register, name='register'),
]