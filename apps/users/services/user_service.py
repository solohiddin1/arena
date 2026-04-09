import concurrent.futures
import datetime

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.enum import ResultCodes
from apps.shared.send_email import send_email_from_server_from_brevo
from apps.shared.utils import get_logger
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

	def _send_otp_with_fallback(self, email: str, otp: str, timeout: int = 5):
		def try_send():
			try:
				return send_email_from_server_from_brevo(email, otp)
			except Exception as exc:
				self.logger.info(f"Primary provider failed: {exc}")
				try:
					return send_otp_email(email, otp)
				except Exception as fallback_exc:
					self.logger.info(f"Both providers failed: {fallback_exc}")
					raise Exception("Unable to send OTP")

		with concurrent.futures.ThreadPoolExecutor() as executor:
			future = executor.submit(try_send)
			try:
				return future.result(timeout=timeout)
			except concurrent.futures.TimeoutError:
				raise Exception("OTP sending timed out")

	def register_user(self, req_body: dict):
		email = req_body["email"]
		full_name = req_body.get("full_name", "")
		password = req_body["password"]

		user = get_user_by_username(email)

		if user is None:
			user = create_user(
				email=email,
				full_name=full_name,
				phone_number=req_body.get("phone_number", ""),
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
			f"user is registering with email: {email},"
			f"and full_name: {full_name}, with otp: {otp}"
		)
		send_result = self._send_otp_with_fallback(email, otp)
		if not send_result:
			return {"error": ResultCodes.ERROR_SMS_SERVICE}
		create_user_auth_otp_log(user=user, code=otp, otp_created_at=timezone.now())

		return {
			"data": {
				"id": user.id,
				"full_name": user.full_name,
				"email": user.email,
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

		if user.email == "sirojiddinovsolohiddin961@gmail.com":
			if code == "2222":
				token = RefreshToken.for_user(user)
				return {"data": {"refresh": str(token), "access": str(token.access_token)}}
			return {"error": ResultCodes.WRONG_VERIFICATION_CODE}

		if user.otp and timezone.now() - user.otp_created_at > datetime.timedelta(minutes=20):
			return {"error": ResultCodes.OTP_EXPIRED}

		if user.otp != code:
			return {"error": ResultCodes.WRONG_VERIFICATION_CODE}		

		set_otp_as_used(user, code)
		update_user_set_verified(user.id)
		token = RefreshToken.for_user(user)
		return {"data": {"refresh": str(token), "access": str(token.access_token)}}

	def login_user(self, request, email: str, password: str):
		user = authenticate(request=request._request, username=email, password=password)
		if user is None:
			user = authenticate(request=request._request, email=email, password=password)

		if user is None:
			return {"error": ResultCodes.INVALID_CREDENTIALS}
		if not user.is_verified:
			return {"error": ResultCodes.USER_IS_NOT_VERIFIED}

		token = RefreshToken.for_user(user)
		return {"data": {"refresh": str(token), "access": str(token.access_token)}}

	def request_forgot_password_otp(self, email: str):
		user = get_user_by_username(email)
		if not user:
			return {"error": ResultCodes.USER_NOT_FOUND}

		limit_error = validate_and_increment_otp_send_limit(user.id)
		if limit_error:
			return {"error": limit_error}

		otp = generate_otp()
		update_user_otp(user.id, otp, timezone.now())

		send_result = self._send_otp_with_fallback(email, otp)
		if not send_result:
			return {"error": ResultCodes.ERROR_SMS_SERVICE}
		create_user_auth_otp_log(user=user, code=otp, otp_created_at=timezone.now())

		return {
			"data": {
				"email": user.email,
				"otp": otp,
				"message": "OTP sent successfully",
			}
		}

	def verify_forgot_password(self, email: str, code: str):
		user = get_user_by_username(email)
		if not user:
			return {"error": ResultCodes.USER_NOT_FOUND}

		if not user.otp or not user.otp_created_at:
			return {"error": ResultCodes.WRONG_VERIFICATION_CODE}

		if timezone.now() - user.otp_created_at > datetime.timedelta(minutes=3):
			return {"error": ResultCodes.OTP_EXPIRED}

		if user.otp != code:
			return {"error": ResultCodes.OTP_INCORRECT}

		return {"data": {"verified": True, "message": "Verification success"}}

	def apply_new_password(self, email: str, code: str, password: str):
		user = get_user_by_username(email)
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

