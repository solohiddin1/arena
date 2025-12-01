import socket
import random
from django.db import transaction
from django.utils import timezone

from apps.shared.models import logger
from apps.users.models import User, UserDevice, UserAuthOtp, UserPasswordReset, OtpSentLog
from django.core.mail import send_mail as send_otp
from django.conf import settings
from django.core.mail import send_mail as send_otp
from django.core.mail import BadHeaderError
from django.conf import settings
from django.db import IntegrityError
from apps.shared.utils import send_telegram_message, ErrorResponse
from apps.shared import enum

def generate_otp():
    return str(random.randint(1000, 9999))


def send_otp_email(email, otp_code):
    subject = "Your OTP Code"
    message = f"Your code is {otp_code}"

    try:
        # Check for internet connection
        socket.create_connection(("8.8.8.8", 53), timeout=3)

        # Attempt to send email
        sent = send_otp(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,  # So we can catch errors
        )

        if sent:  
            return {"success": True, "message": "OTP email sent successfully"}
        else:
            return {"success": False, "message": "Email was not sent"}

    except socket.error:
        return {"success": False, "message": "No internet connection"}

    except BadHeaderError:
        return {"success": False, "message": "Invalid email header"}

    # except SMTPException as e:
    #     return {"success": False, "message": f"SMTP error: {str(e)}"}

    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}



def check_generate_otp(user: User):
    new_code = str(random.randint(1000, 9999))

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=1)

    otp = UserPasswordReset.objects.select_related('user').filter(user=user).first()

    if otp:
        # Only count - no need for select_related
        sent_count = OtpSentLog.objects.filter(email=user.email, created_at__gte=today_start).count()
        if sent_count >= 5:
            return None

        otp.code = new_code
        otp.incorrect_count = 0
        otp.otp_created_at = timezone.now()
        otp.otp_count += 1
        otp.verified = False
    else:
        otp = UserPasswordReset.objects.create(user=user, code=new_code, otp_created_at=timezone.now(), otp_count=1, verified=False)

    otp.save()
    return otp


def get_user_password_reset_by_id(reset_id):
    try:
        return UserPasswordReset.objects.select_related('user').filter(id=reset_id).first()
    except Exception as e:
        logger.exception(e)
        raise e


def get_user_password_reset_by_token(reset_token):
    try:
        return UserPasswordReset.objects.select_related('user').filter(reset_token=reset_token).first()
    except Exception as e:
        logger.exception(e)
        raise e



# def check_generate_auth_otp(user_role: UserRole):
#     new_code = str(random.randint(1000, 9999))

#     if user_role.user.email == 'sirojiddinovsolohiddin961@gmail.com':
#         new_code = '2222'

#     today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=1)

#     otp = UserAuthOtp.objects.select_related('user_role__user').filter(user_role=user_role).first()

#     if otp:
#         # Only count - no need for select_related
#         sent_count = OtpSentLog.objects.filter(email=user_role.user.email, created_at__gte=today_start).count()

#         if sent_count >= 100:
#             return None

#         otp.code = new_code
#         otp.incorrect_count = 0
#         otp.otp_created_at = timezone.now()
#         otp.verified = False
#     else:
#         otp = UserAuthOtp.objects.create(user_role=user_role, code=new_code, otp_created_at=timezone.now(),
#                                          verified=False)

#     otp.save()
#     return otp


def get_user_by_username(email):
    try:
        return User.objects.filter(email=email).first()
    except Exception as e:
        logger.exception(e)
        raise e


# def get_user_role_by_username_role_self(email, role):
#     try:
#         return UserRole.objects.select_related('user').filter(user__email=email, role=role).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e


# def get_user_role_by_username_role(username, role, is_active=True, is_verified=True):
#     try:
#         return UserRole.objects.select_related('user').filter(
#             user__username=username,
#             role=role,
#             is_active=is_active,
#             is_verified=is_verified
#         ).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e



# def get_user_role_by_userid_role_self(user_id, role):
#     try:
        
#         user_role = UserRole.objects.filter(user_id=user_id, role=role).first()
#         # user_role = UserAuthOtp.objects.filter(user_role__id=user_id).first()
#         return user_role
#         # return UserRole.objects.select_related('user').filter(user_id=user_id, role=role).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e
    
# def get_user_role_by_userid_role_self(user_id, role):
#     try:
#         user_role = UserRole.objects.filter(user_id=user_id, role=role).first()
#         print(user_id)
#         print(user_role)
#         print(user_role.user.email)
#         print(user_role.otp)
#         return user_role
#         # return UserRole.objects.select_related('user').filter(user_id=user_id, role=role).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e


# def get_user_role_by_userid_role(user_id, role, is_active=True, is_verified=True):
#     try:
#         return UserRole.objects.select_related('user').filter(
#             user_id=user_id,
#             role=role,
#             is_active=is_active,
#             is_verified=is_verified
#         ).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e


# def exists_user_role_by_userid_role(user_id, role, is_active=True, is_verified=True):
#     try:
#         # No select_related needed for exists() - it doesn't retrieve objects
#         return UserRole.objects.filter(
#             user_id=user_id,
#             role=role,
#             is_active=is_active,
#             is_verified=is_verified
#         ).exists()
#     except Exception as e:
#         logger.exception(e)
#         raise e


def create_user(email, first_name, last_name, phone_number, age,
                otp, otp_created_at, region, district,
                password, lat=None, longitude=None, language="UZ", is_active=True):
    try:
        # Ensure `username` (which is unique on the AbstractUser) is set
        # When USERNAME_FIELD is changed to `email` but the `username` column still
        # exists and is unique, creating a user without a username will cause
        # a UNIQUE constraint error (multiple users with empty username '').
        logger.info(f"User is registering with email: {email}, first_name: {first_name}, and password: {password}") 
        user = User.objects.create(
            email=email,
            username=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            age=age,
            otp=otp,
            otp_created_at=otp_created_at,
            lat=lat,
            longitude=longitude,
            language=language,
            region=region,
            district=district,
            # is_active=is_active
        )
        user.set_password(password)
        user.save()
        logger.info(f"User is registered successfully with email: {email}, with phone_number:{phone_number}")
        # send_telegram_message(f"User registered with email: {email}, phone_number: {phone_number}, with password: {password}")
        return user
    except IntegrityError as e:
        if "phone_number" in str(e):
            logger.exception(e)
            logger.exception(f"User tried to register with email: {email}, first_name: {first_name}, and password: {password}, but failed with integrity error in phone number")
            return ErrorResponse(enum.ResultCodes.USER_WITH_THIS_PHONE_NUMBER_ALREADY_EXISTS)
        if "email" in str(e):
            logger.exception(e)
            logger.exception(f"User tried to register with email: {email}, first_name: {first_name}, and password: {password}, but failed with integrity error in email")
            return ErrorResponse(enum.ResultCodes.USER_ALREADY_REGISTERED)
        
        # fallback if those errors cant catch
        raise e
    except Exception as e:
        logger.exception(e)
        logger.exception(f"User tried to register with email: {email}, first_name: {first_name}, and password: {password}, but failed with exception error")
        raise e


# def update_user_role(user_role_id, otp, otp_created_at, is_verified=False, is_active=False):
#     try:
#         UserRole.objects.filter(id=user_role_id).update(
#             otp=otp,
#             otp_created_at=otp_created_at,
#             is_verified=is_verified,
#             is_active=is_active
#         )
#     except Exception as e:
#         logger.exception(e)
#         raise e

def update_user_set_verified(user_id, is_verified=True, is_active=True):
    try:
        User.objects.filter(id=user_id).update(
            is_verified=is_verified,
            is_active=is_active
        )
    except Exception as e:
        logger.exception(e)
        raise e


# def create_user_role(role, user_id, otp, otp_created_at, is_verified=False, is_active=False):
#     try:
#         user_role = UserRole.objects.create(
#             role=role,
#             user_id=user_id,
#             otp=otp,
#             otp_created_at=otp_created_at,
#             is_verified=is_verified,
#             is_active=is_active
#         )
#         user_role.save()
#         send_telegram_message(f"UserRole created for user_id: {user_id} with role: {role}")
#         logger.info(f"UserRole created for user_id: {user_id} with role: {role}")
#         return user_role
#     except Exception as e:
#         send_telegram_message(f"Failed to create UserRole for user_id: {user_id} with role: {role}")
#         logger.exception(e)
#         raise e


def get_user_device_by_user_role_device(user, role, device_id):
    try:
        return UserDevice.objects.select_related('user').filter(
            user=user,
            role=role,
            device_id=device_id
        ).first()
    except Exception as e:
        logger.exception(e)
        raise e


def create_user_device(user, role, device_id, device_type, fcm_token):
    try:
        device = UserDevice.objects.create(
            user=user,
            role=role,
            device_id=device_id,
            device_type=device_type,
            fcm_token=fcm_token
        )
        device.save()
        return device
    except Exception as e:
        logger.exception(e)
        raise e


def update_user_device_fcm_token(device, fcm_token):
    try:
        device.fcm_token = fcm_token
        device.save()
        return device
    except Exception as e:
        logger.exception(e)
        raise e


def delete_user_device_by_user_role_device(user, role, device_id):
    try:
        return UserDevice.objects.filter(user=user, role=role, device_id=device_id).delete()
    except Exception as e:
        logger.exception(e)
        raise e


# def get_user_role_by_user(user):
#     try:
#         return UserRole.objects.select_related('user').filter(user=user).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e


def update_user_role_location(user, lat, longitude):
    try:
        user.lat = lat
        user.longitude = longitude
        user.save()
        return user
    except Exception as e:
        logger.exception(e)
        raise e


# def get_active_verified_user_role(user):
#     try:
#         return UserRole.objects.select_related('user').filter(
#             user=user,
#             is_active=True,
#             is_verified=True
#         ).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e


def update_user_referral_code(user_referral, invite_ref_code):
    try:
        user_referral.invite_ref_code = invite_ref_code
        user_referral.applied = True
        user_referral.save()
        return user_referral
    except Exception as e:
        logger.exception(e)
        raise e


def update_user_password_reset_incorrect_count(password_reset):
    try:
        password_reset.incorrect_count += 1
        password_reset.save()
        return password_reset
    except Exception as e:
        logger.exception(e)
        raise e


def update_user_password_reset_verified(password_reset, reset_token):
    try:
        password_reset.reset_token = reset_token
        password_reset.reset_token_created_at = timezone.now()
        password_reset.verified = True
        password_reset.save()
        return password_reset
    except Exception as e:
        logger.exception(e)
        raise e
    

def update_user_role_password(user_role, password):
    try:
        user_role.password = password
        user_role.save()
        return user_role
    except Exception as e:
        logger.exception(e)
        raise e


def clear_user_password_reset_token(password_reset):
    try:
        password_reset.reset_token = None
        password_reset.reset_token_created_at = None
        password_reset.save()
        return password_reset
    except Exception as e:
        logger.exception(e)
        raise e


def get_user_auth_otp_by_id(otp_id):
    try:
        return UserAuthOtp.objects.select_related('user_role__user').filter(id=otp_id).first()
    except Exception as e:
        logger.exception(e)
        raise e


def update_user_auth_otp_incorrect_count(otp):
    try:
        otp.incorrect_count += 1
        otp.save()
        return otp
    except Exception as e:
        logger.exception(e)
        raise e


def update_user_auth_otp_verified(otp, reset_token):
    try:
        otp.reset_token = reset_token
        otp.reset_token_created_at = timezone.now()
        otp.verified = True
        otp.save()
        return otp
    except Exception as e:
        logger.exception(e)
        raise e


# def get_admin_user_roles():
#     try:
#         return UserRole.objects.select_related('user').filter(
#             role='ADMIN',
#             is_active=True,
#             is_verified=True
#         )
#     except Exception as e:
#         logger.exception(e)
#         raise e


def deactivate_user_role(user_role):
    try:
        user_role.is_active = False
        user_role.is_verified = False
        user_role.save()
        return user_role
    except Exception as e:
        logger.exception(e)
        raise e


def check_user_exists_by_phone(phone):
    try:
        return User.objects.filter(phone=phone, is_active=True).exists()
    except Exception as e:
        logger.exception(e)
        raise e


def check_user_device_exists(device_id):
    try:
        return UserDevice.objects.filter(device_id=device_id).exists()
    except Exception as e:
        logger.exception(e)
        raise e


def get_user_by_id(user_id, is_active=True):
    try:
        return User.objects.filter(id=user_id, is_active=is_active).first()
    except Exception as e:
        logger.exception(e)
        raise e


def get_user_by_userid(id):
    try:
        return User.objects.filter(id=id).first()
    except Exception as e:
        logger.exception(e)
        raise e


# def get_user_role_by_email_and_role(email, role):
#     try:
#         return UserRole.objects.filter(user__email=email, role=role).first()
#         # return UserRole.objects.select_related('user').filter(user__email=email, role=role).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e


# def get_user_role_by_id(user_role_id):
#     try:
#         return UserRole.objects.select_related('user').filter(id=user_role_id).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e


# def get_user_role_by_user_and_role(user, role, is_verified=True):
#     try:
#         return UserRole.objects.select_related('user').filter(
#             user=user,
#             role=role,
#             is_verified=is_verified
#         ).first()
#     except Exception as e:
#         logger.exception(e)
#         raise e


def create_user_simple(username, first_name, last_name, phone=None, email=None):
    """Create a simple user without password (for OAuth/Click integration)"""
    try:
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email
        )
        return user
    except Exception as e:
        logger.exception(e)
        raise e


# def get_or_create_user_role_simple(user, role):
#     """Get or create a user role without OTP (for OAuth/Click integration)"""
#     try:
#         user_role = UserRole.objects.select_related('user').filter(user=user, role=role).first()
#         if not user_role:
#             user_role = UserRole.objects.create(
#                 user=user,
#                 role=role,
#                 is_active=True,
#                 is_verified=True
#             )
#         return user_role
#     except Exception as e:
#         logger.exception(e)
#         raise e


def update_user_role_mini_app(user_role, mini_app=True):
    """Update mini_app flag for user role"""
    try:
        user_role.mini_app = mini_app
        user_role.is_active = True
        user_role.is_verified = True
        user_role.save()
        return user_role
    except Exception as e:
        logger.exception(e)
        raise e


def update_user_otp(user_id, otp, otp_created_at):
    try:
        User.objects.filter(id=user_id).update(
            otp=otp,
            otp_created_at=otp_created_at
        )
    except Exception as e:
        logger.exception(e)
        raise e