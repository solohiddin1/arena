from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.status import HTTP_400_BAD_REQUEST
from app.serializers_f.user_serializer import UserSerializer
from app.models import User
from rest_framework import permissions
from rest_framework.decorators import api_view, APIView, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login as django_login
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.cache import cache
# from drf_yasg.utils import swagger_auto_schema
from app.serializers_f.email_serializers import SendEmail, LoginSerializer
from app.serializers_f.user_serializer import LoginUserSerializer, ChangePasswordSerializer
# from app.serializers_f.student_serizlizer import StudentSerializer


# #@swagger_auto_schema(method='post', request_body=LoginSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
        serializer = LoginSerializer(data=request.data)
        email = request.data.get("email")
        # password = request.data.get("password")

        # user = authenticate(request, email=email, password=password)
        if email is not None:
            otp = random.randint(1000, 9999)
            cache.set(email, otp, timeout=300)

            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}. It is valid for 5 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({'success': True, 'message': 'OTP sent to email.'})
        

        return Response({'success': False, 'message': 'Invalid credentials.'}, status=400)


#@swagger_auto_schema(method='post',request_body=SendEmail)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify(request):

        seializer = SendEmail(data=request.data)
        seializer.is_valid(raise_exception=True)
        email = seializer.validated_data['email']
        otp = request.data.get('otp')

        cached_otp = cache.get(email)
        if cached_otp and str(cached_otp) == str(otp):
            cache.delete(email)

            user = User.objects.filter(email=email).first()
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({'success': True, 'access': str(refresh.access_token), 'refresh': str(refresh)})

            return Response({'success': False, 'message': 'Invalid user.'}, status=400)

        return Response({'success': False, 'message': 'Invalid or expired OTP.'}, status=400)
   

def userlogin_view(request):
    return render(request,'login.html')


#@swagger_auto_schema(method='post', request_body=LoginUserSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def userlogin(request):
    # Handle both JSON and form data
    if request.content_type == 'application/json':
        data = request.data
    else:
        data = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password')
        }
    
    serializer = LoginUserSerializer(data=data)
    print('user here')
    if serializer.is_valid():
        print('user here2 ---')
        email = serializer.validated_data.get("email", "").strip().lower()
        password = serializer.validated_data.get("password", "").strip()
        print(email,password,'email password ---')
        print(f"[{email}], [{password}]")
        user = authenticate(request, email=email, password=password)
        print(user)
        if user:
            otp = random.randint(1000, 9999)
            cache.set(email,otp,timeout=300)
            print("start email")
            send_mail(
                 "Your code sent",
                    f"Your code is {otp}. It is valid for 5 minutes.",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
            )
            # token, created = Token.objects.get_or_create(user=user)
            return Response({'success': True, 'message': 'OTP sent to email.'},status=status.HTTP_200_OK)
        return Response({'success': False, 'message': 'Invalid credentials.'}, status=400)
    return Response(serializer.errors, status=400)

def verify_user_email_view(request):
    return render(request,'verify_otp.html')

#@swagger_auto_schema(method='post', request_body=SendEmail)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_user_email(request):
    serializer = SendEmail(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    otp = request.data.get('otp')

    cached_otp = cache.get(email)
    print(cached_otp)
    print('user is being verified')
    if cached_otp and str(cached_otp) == str(otp):
        print("email cache")
        cache.delete(email)

        user = User.objects.filter(email=email).first()
        if user:
            user.email_verified = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({'success': True, 'message':'email verifikatsiyadan otdi', 'access': str(refresh.access_token), 'refresh': str(refresh)})

        return Response({'success': False, 'message': 'Invalid user.'}, status=400)

    return Response({'success': False, 'message': 'Invalid or expired OTP.'}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    # Expect refresh token in body and blacklist it
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"success": False, "error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"success": True, "message": "Logged out successfully"})
    except Exception as exc:
        return Response({"success": False, "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

#@swagger_auto_schema(method='post', request_body=ChangePasswordSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def change_password(request):
    print('111111')

    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    old_password = serializer.validated_data['old_password']
    new_password = serializer.validated_data['new_password']
    confirm_password = serializer.validated_data['confirm_password']
    print(new_password)
    print('user changing password')

    try:
        user1 = User.objects.get(email=email)
    
    except Exception as e:
        print(e)
        return Response({"error":str(e)})
    print(user1)
    if old_password == new_password:
        return Response({"message":"please enter new password"},status=status.HTTP_400_BAD_REQUEST)
    if new_password != confirm_password:
        return Response({"message":"new password should match to confirm password!"},status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request._request,email=email,password=old_password)
    print(user)
    if user is None:
        return Response({"error":"Password is incorrect"},status=status.HTTP_400_BAD_REQUEST)
    if user:
        print('user here!')
        if not user1.email_verified:
            return Response({'success': False, 'message': 'email not verified'}, status=HTTP_400_BAD_REQUEST)
        
        print(f"user { user}")
        
        if user:
            user.set_password(new_password)
            user.is_active = True
            user.save()
            django_login(request._request, user)  # Log the user in
            refresh = RefreshToken.for_user(user)
            return Response({'success': True, 'message': 'Password changed successfully.', 'access': str(refresh.access_token), 'refresh': str(refresh)})

        return Response({"success":False, "errors" : serializer.errors},status=400)
    else:
        return Response({"error":"password is incorrect"},status=status.HTTP_400_BAD_REQUEST)


# @permission_classes(IsAuthenticated)
# def change_password_page(request):
#     return render(request,'change_password.html')


# #@swagger_auto_schema(method='post', request_body=LoginSerializer)
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def forgot_password(request):
    serializer = LoginSerializer(data=request.data)
    
    print(request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except Exception as e:
            return Response({"error":str(e)})
        if user:
            otp = random.randint(1000,9999)
            cache.set(email,otp,timeout=300)
            print("otp sent")
            send_mail(
                 "Your code sent",
                    f"Your code is {otp}. It is valid for 5 minutes.",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                    )
            return Response({"message":"please verify your email, we sent code to your email"}) 
        return Response({"error":"User not found"})
    return Response({"error":serializer.errors})





# from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from app.utils import generate_reset_password_link

token_generator = PasswordResetTokenGenerator()

def forgot_password_view(request):
    return render(request,'forgot_password.html')

#@swagger_auto_schema(method='post',request_body=LoginSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
        reset_link = generate_reset_password_link(user, request)
        # TODO: send reset_link by email (SendGrid, SMTP, etc.)
        send_mail(
                 "Reset your password ",
                    f"Your reset password link. {reset_link}",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
            )
        return Response({"reset_link": reset_link})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

from rest_framework import serializers

class Reset(serializers.Serializer):
    new_password = serializers.CharField()
    conf_password = serializers.CharField()


@permission_classes([AllowAny])
#@swagger_auto_schema(method='post',request_body=Reset)
@api_view(['POST'])
def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        print(user)
        print(user.email)
    except Exception:
        return Response({"error": "Invalid link"}, status=400)

    if token_generator.check_token(user, token):
        new_password = request.data.get("password")
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful","password":new_password})
    return Response({"error": "Invalid or expired token"}, status=400)


def reset_page(request,uiid64,token):
    if request.method == 'POST':
        password = request.POST.get("password")
        conf_password = request.POST.get("conf_password")

        if password != conf_password:
            return render(request,'reset_password.html',{
                "error":"passwords dont match",
                "uiid64":uiid64,
                "token":token
                }
            )
        try:
            uid = urlsafe_base64_decode(uiid64).decode()
            user = User.objects.get(pk=uid)
        except Exception as e:
            return render(request,'reset_password.html',{"error":"Invalid link"})

        if default_token_generator.check_token(user,token):
            user.set_password(conf_password)
            user.save()
            return redirect('home')
        else:
            return render(request,'reset_password.html',{"error":"Token expired"})
        
    return render(request,'reset_password.html',{"uiid64":uiid64,"token":token})


# @permission_classes(IsAuthenticated)
from django.contrib.auth.decorators import login_required

# @login_required
# @login_required(login_url='/userlogin/')

# @api_view(["GET"])
@permission_classes([IsAuthenticated])
def home(request):
    return render(request,"home.html")

def loginexistinguser_view(request):
    return render(request,'loginexisting.html')
    

@permission_classes([IsAuthenticated])
def student_dashboard(request):
    return render(request,'student_dashboard.html')


#@swagger_auto_schema(method='post', request_body=LoginUserSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def loginexistinguser(request):
    serializer = LoginUserSerializer(data=request.data)
    print('user here')
    if serializer.is_valid():
        print('user here2 ---')
        email = serializer.validated_data.get("email", "").strip().lower()
        try:
            userin = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error":"User not found"})
        # if userin is None:
        #     return Response({"error":"User not found!"},status=status.HTTP_404_NOT_FOUND)
        password = serializer.validated_data.get("password", "").strip()
        print(email,password,'email password ---')
        
        user = authenticate(request=request._request, email=email, password=password)
        print(user,'tthis user is good')
        print(userin,'userin -------- here ')
        if user is None:
            return Response({"error":"Invalid credentials"},status=status.HTTP_400_BAD_REQUEST)
        if not userin.email_verified:
            return Response({"error": "email is not verified"}, status=status.HTTP_400_BAD_REQUEST)
    
        if user:
            django_login(request._request, user)  # Log the user in
            refresh = RefreshToken.for_user(user)
            role = 'admin' if userin.is_admin  else 'User' 
            refresh['role'] = role
            print(role)
            print(refresh)
            return Response({
                'success': True, 
                'message': 'user logged in successfully.', 
                'role': role,
                'access': str(refresh.access_token), 
                'refresh': str(refresh)})
        
        return Response({'success': False, 'message': 'Invalid credentials.'}, status=400)
    return Response(serializer.errors, status=400)