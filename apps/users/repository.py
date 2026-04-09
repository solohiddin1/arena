import socket
import random
import datetime
from django.db import transaction
from django.utils import timezone

from apps.shared.middleware.middleware import get_logger
from apps.users.models import User, UserDevice, UserAuthOtp
from django.core.mail import send_mail as send_otp
from django.conf import settings
from django.core.mail import send_mail as send_otp
from django.core.mail import BadHeaderError
from django.conf import settings
from django.db import IntegrityError
from apps.shared.utils import send_telegram_message, ErrorResponse
from apps.shared import enum

logger = get_logger()

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

    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}



def get_user_by_username(email):
    try:
        return User.objects.filter(email=email).first()
    except Exception as e:
        logger.exception(e)
        raise e


def create_user(email, full_name, phone_number,
                otp, otp_created_at,password):
    try:
        # Ensure `username` (which is unique on the AbstractUser) is set
        # When USERNAME_FIELD is changed to `email` but the `username` column still
        # exists and is unique, creating a user without a username will cause
        # a UNIQUE constraint error (multiple users with empty username '').
        logger.info(f"User is registering with email: {email}, full_name: {full_name}, and password: {password}") 
        user = User.objects.create(
            email=email,
            username=email,
            full_name=full_name,
            phone_number=phone_number,
            otp=otp,
            otp_created_at=otp_created_at,
            is_active=True,
        )
        user.set_password(password)
        user.save()
        logger.info(f"User is registered successfully with email: {email}, with phone_number:{phone_number}")
        # send_telegram_message(f"User registered with email: {email}, phone_number: {phone_number}, with password: {password}")
        return user
    except IntegrityError as e:
        if "phone_number" in str(e):
            logger.exception(e)
            logger.exception(f"User tried to register with email: {email}, full_name: {full_name}, and password: {password}, but failed with integrity error in phone number")
            return ErrorResponse(enum.ResultCodes.USER_WITH_THIS_PHONE_NUMBER_ALREADY_EXISTS)
        if "email" in str(e):
            logger.exception(e)
            logger.exception(f"User tried to register with email: {email}, full_name: {full_name}, and password: {password}, but failed with integrity error in email")
            return ErrorResponse(enum.ResultCodes.USER_ALREADY_REGISTERED)
        
        # fallback if those errors cant catch
        raise e
    except Exception as e:
        logger.exception(e)
        logger.exception(f"User tried to register with email: {email}, full_name: {full_name}, and password: {password}, but failed with exception error")
        raise e


def update_user_set_verified(user_id, is_verified=True, is_active=True):
    try:
        User.objects.filter(id=user_id).update(
            is_verified=is_verified,
            is_active=is_active
        )
    except Exception as e:
        logger.exception(e)
        raise e



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


def update_user_referral_code(user_referral, invite_ref_code):
    try:
        user_referral.invite_ref_code = invite_ref_code
        user_referral.applied = True
        user_referral.save()
        return user_referral
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


def create_user_simple(username, full_name, phone=None, email=None):
    """Create a simple user without password (for OAuth/Click integration)"""
    try:
        user = User.objects.create(
            username=username,
            full_name=full_name,
            phone=phone,
            email=email
        )
        return user
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


def validate_and_increment_otp_send_limit(user_id: int):
    try:
        now = timezone.now()
        user = User.objects.filter(id=user_id).first()
        if user is None:
            return enum.ResultCodes.USER_ROLE_NOT_FOUND

        latest_otp = UserAuthOtp.objects.filter(user=user).order_by("-otp_created_at").first()
        if latest_otp and latest_otp.otp_created_at:
            if (now - latest_otp.otp_created_at).total_seconds() < 40:
                return enum.ResultCodes.OTP_ALREADY_SENT

        hour_start = now - datetime.timedelta(hours=1)
        hour_count = UserAuthOtp.objects.filter(user=user, otp_created_at__gte=hour_start).count()
        if hour_count >= 5:
            return enum.ResultCodes.OTP_HOURLY_LIMIT_REACHED

        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_count = UserAuthOtp.objects.filter(user=user, otp_created_at__gte=day_start).count()
        if day_count >= 10:
            return enum.ResultCodes.OTP_DAILY_LIMIT_REACHED

        return None
    except Exception as e:
        logger.exception(e)
        raise e


def create_user_auth_otp_log(user: User, code: int | str, otp_created_at):
    try:
        return UserAuthOtp.objects.create(
            user=user,
            code=int(code),
            otp_created_at=otp_created_at,
            is_used=False,
            incorrect_count=0,
            verified=False,
        )
    except Exception as e:
        logger.exception(e)
        raise e
    
def set_otp_as_used(user: User, code: int):
    try:
        otp = UserAuthOtp.objects.filter(user=user, code=int(code)).first()
        if not otp:
            raise ValueError("OTP not found")
        otp.is_used = True
        otp.verified = True
        otp.save()
        return otp
    except Exception as e:
        logger.exception(e)
        raise e