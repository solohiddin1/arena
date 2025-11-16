from django.urls import path
# from app.views.user import UserRegisterView , DeleteUser, GetAllUsers

from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
# from apps.app.views.arena import ArenaCreateView, ArenaListView
# from apps.app.views import OwnerProfileView, OwnerRegisterView

urlpatterns = [
    # mock data
    
    # owner
    # path('owner_register/',OwnerRegisterView.as_view(),name='register_owner'),
    # path('get_owner/',OwnerProfileView.as_view(),name='get_owner'),

    # path('add_arena/',ArenaCreateView.as_view(),name='add_arena'),
    # path('arena/<int:pk>/',ArenaListView.as_view(),name='arena_detail'),

    # users

    # login
    
    # token
    path('token/',TokenObtainPairView.as_view()),
    path('token/refresh/',TokenRefreshView.as_view()),

    # path('',home, name='home'),

]