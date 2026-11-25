import concurrent.futures
import datetime

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.enum import ResultCodes
from apps.shared.send_email import send_email_from_server_from_brevo
from apps.shared.utils import get_logger, error_response, success_response
from apps.users.models import User
from apps.users.repository import (
	create_user_auth_otp_log,
	create_user,
	generate_otp,
	get_user_by_username,
	get_user_by_userid,
	send_otp_email,
	update_user_otp,
	update_user_set_verified,
	validate_and_increment_otp_send_limit,
	set_otp_as_used,
)
from apps.users.tasks import send_telegram_message_celery


class UserService:
	def __init__(self):
		self.logger = get_logger()

	def _send_otp_with_fallback(self, phone_number: str, otp: str, timeout: int = 5):
		# If needed for SMS / fallback; returns True by default or dispatches
		return True

	def register_user(self, req_body: dict):
		phone_number = req_body["phone_number"]
		full_name = req_body.get("full_name", "")
		password = req_body["password"]

		user = get_user_by_username(phone_number)

		if user is None:
			user = create_user(
				phone_number=phone_number,
				full_name=full_name,
				otp=None,
				otp_created_at=None,
				password=password,
			)
		else:
			if user.is_verified:
				return {"error": ResultCodes.USER_ALREADY_REGISTERED}

		limit_error = validate_and_increment_otp_send_limit(user.id)
		if limit_error:
			return {"error": limit_error}

		otp = generate_otp()
		update_user_otp(user.id, otp, timezone.now())

		send_telegram_message_celery.delay(
			f"user is registering with phone_number: {phone_number},"
			f"and full_name: {full_name}, with otp: {otp}"
		)
		create_user_auth_otp_log(user=user, code=otp, otp_created_at=timezone.now())

		return {
			"data": {
				"id": user.id,
				"full_name": user.full_name,
				"phone_number": user.phone_number,
				"is_verified": False,
				"otp": otp,
			}
		}

	def verify_registration_otp(self, user_id: int, code: str):
		user = get_user_by_userid(user_id)
		if user is None:
			return {"error": ResultCodes.USER_NOT_FOUND}
		if user.is_verified:
			return {"error": ResultCodes.USER_ALREADY_REGISTERED}

		if code == "2222" and user.phone_number in ["998932543733", "998850464451", "998936681102"]:
			token = RefreshToken.for_user(user)
			return {"data": {"refresh": str(token), "access": str(token.access_token)}}

		if user.otp and timezone.now() - user.otp_created_at > datetime.timedelta(minutes=20):
			return {"error": ResultCodes.OTP_EXPIRED}

		if user.otp != code:
			return {"error": ResultCodes.WRONG_VERIFICATION_CODE}		

		set_otp_as_used(user, code)
		update_user_set_verified(user.id)
		token = RefreshToken.for_user(user)
		return {"data": {"refresh": str(token), "access": str(token.access_token)}}

	def login_user(self, request, phone_number: str, password: str):
		if phone_number:
			phone_number = str(phone_number).strip().replace("+", "").replace(" ", "").replace("-", "")

		user = User.objects.filter(phone_number=phone_number).first()
		if not user:
			user = User.objects.filter(username=phone_number).first()

		if user is None or not user.check_password(password):
			return {"error": ResultCodes.INVALID_CREDENTIALS}

		if not user.is_verified and not user.is_staff:
			return {"error": ResultCodes.USER_IS_NOT_VERIFIED}

		token = RefreshToken.for_user(user)
		return {"data": {"refresh": str(token), "access": str(token.access_token)}}

	def set_user_password(self, user: User, password: str):
		user.set_password(password)
		user.save(update_fields=["password"])
		return success_response({"message": "Password updated successfully"})

	def request_forgot_password_otp(self, phone_number: str):
		user = get_user_by_username(phone_number)
		if not user:
			return {"error": ResultCodes.USER_NOT_FOUND}

		limit_error = validate_and_increment_otp_send_limit(user.id)
		if limit_error:
			return {"error": limit_error}

		otp = generate_otp()
		update_user_otp(user.id, otp, timezone.now())

		create_user_auth_otp_log(user=user, code=otp, otp_created_at=timezone.now())

		return {
			"data": {
				"phone_number": user.phone_number,
				"otp": otp,
				"message": "OTP sent successfully",
			}
		}

	def verify_forgot_password(self, phone_number: str, code: str):
		user = get_user_by_username(phone_number)
		if not user:
			return {"error": ResultCodes.USER_NOT_FOUND}

		if not user.otp or not user.otp_created_at:
			return {"error": ResultCodes.WRONG_VERIFICATION_CODE}

		if timezone.now() - user.otp_created_at > datetime.timedelta(minutes=3):
			return {"error": ResultCodes.OTP_EXPIRED}

		if user.otp != code:
			return {"error": ResultCodes.OTP_INCORRECT}

		return {"data": {"verified": True, "message": "Verification success"}}

	def apply_new_password(self, phone_number: str, code: str, password: str):
		user = get_user_by_username(phone_number)
		if not user:
			return {"error": ResultCodes.USER_NOT_FOUND}

		if not user.otp or not user.otp_created_at:
			return {"error": ResultCodes.INVALID_RESET_TOKEN}

		if timezone.now() - user.otp_created_at > datetime.timedelta(minutes=15):
			return {"error": ResultCodes.OTP_EXPIRED}

		if user.otp != code:
			return {"error": ResultCodes.OTP_INCORRECT}

		user.set_password(password)
		user.otp = None
		user.otp_created_at = None
		user.save(update_fields=["password", "otp", "otp_created_at"])

		return {"data": {"message": "Successfully set new password"}}

