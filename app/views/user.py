from django.core.cache import cache
# from linecache import cache
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.status import HTTP_400_BAD_REQUEST
from app.serializers_f.user_serializer import UserSerializer, UserRegisterSerializer
from drf_yasg.utils import swagger_auto_schema
from app.models import User
from rest_framework import permissions
from rest_framework.decorators import api_view, APIView, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
import random


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print('user is registering ')
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            print(user.email,'---')
            # Send OTP
            otp = random.randint(1000, 9999)
            cache.set(user.email, otp, timeout=300)

            send_mail(
                "You are registered",
                f"Please verify your email \n your otp is --> {otp}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({"success": True, "message": "User registered successfully. Please verify your email."}, status=201)
        print(serializer.errors)
        return Response({"Error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)



class CreateUser(APIView):

    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class DeleteUser(APIView):
    permission_classes = [IsAdminUser]
        
    def delete(self, request, pk):
        try:
            print(pk,'1111')
            user = User.objects.get(pk=pk)
            print(user,'---')
            user.delete()
            return Response({"success":True, "message":"User deleted successfully!"},status=200
            )

        except Exception as e:
            print(str(e))
            return Response({"success":False, "error":str(e)}, status=400)