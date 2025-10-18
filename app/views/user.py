from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.status import HTTP_400_BAD_REQUEST
from app.serializers_f.user_serializer import UserSerializer
from drf_yasg.utils import swagger_auto_schema
from app.models import User
from rest_framework import permissions
from rest_framework.decorators import api_view, APIView, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

@permission_classes([IsAdminUser])
def register_view(request):
    return render(request,'register.html')


# @swagger_auto_schema(method='post', request_body=StudentSerializer)
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def register(request):
#     print('user register')
#     serializer = StudentSerializer(data=request.data)

#     if serializer.is_valid():
        
#         # student.is_student = True
#         student = serializer.save()
#         student.save()
#         user = student.user

#         user.is_student = True
#         user.save()
#         print(user.email,'---')
#         # Send OTP
#         # otp = random.randint(1000, 9999)
#         # cache.set(user.email, otp, timeout=300)

#         send_mail(
#             "You are registered",
#             f"you can login using your email and password, Your email is {user.email} , your password is 123456",
#             settings.EMAIL_HOST_USER,
#             [user.email],
#             fail_silently=False,
#         )
#         return Response({"success": True, "message": "User registered successfully."}, status=201)
#     print(serializer.errors)
#     return Response({"Error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)



# class UserCreateView(APIView):
    @swagger_auto_schema(request_body=UserSerializer)
    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="delete", 
    # manual_parameters = [
    #     openapi.Parameter("pk", openapi.IN_PATH, type=openapi.TYPE_INTEGER, required=True)
    #     ] 
    )
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_user(request, pk):
    try:
        print(pk,'1111')
        student = Student.objects.get(pk=pk)
        user = student.user
        print(user,'---')
        print(student,'---')
        student.delete()
        user.delete()
        return Response({"success":True, "message":"User deleted successfully!"},status=200
        )

    except Exception as e:
        print(str(e))
        return Response({"success":False, "error":str(e)}, status=400)