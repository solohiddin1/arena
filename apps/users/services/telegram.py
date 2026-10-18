import secrets
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from apps.shared.middleware.middleware import get_logger
from apps.shared.models import SiteConfig
from apps.users.models import UserAuthOtp
from apps.users.repositories.telegram import TelegramRepo
from apps.users.repositories.user_repo import UserRepo
from apps.users.services.sms import SmsService

logger = get_logger()

SUCCESS_MSG = "✅ Muvaffaqiyatli kirdingiz! Ilovaga qaytishingiz mumkin."
SUCCESS_MSG_WITH_URL = "✅ Muvaffaqiyatli kirdingiz!\n\n👉 Ilovaga qaytish: {url}"
NO_TOKEN_MSG = "Kirish uchun ilovadagi «Telegram orqali kirish» tugmasini bosing."
NO_TOKEN_MSG_WITH_URL = (
    "Kirish uchun ilovadagi «Telegram orqali kirish» tugmasini bosing:\n\n👉 {url}"
)
EXPIRED_MSG = "⚠️ Havola eskirgan yoki yaroqsiz. Iltimos, ilovadan qayta urinib ko'ring."
ASK_PHONE_MSG = "Kirishni yakunlash uchun telefon raqamingizni ulashing 👇"
WRONG_CONTACT_MSG = "Iltimos, o'zingizning telefon raqamingizni ulashing."
OTP_TIME_LIMIT_MSG = "Iltimos otp so'rovi uchun {seconds} sekund kuting"

CONTACT_KEYBOARD = {
    "keyboard": [[{"text": "📱 Telefon raqamni ulashish", "request_contact": True}]],
    "resize_keyboard": True,
    "one_time_keyboard": True,
}
REMOVE_KEYBOARD = {"remove_keyboard": True}


class TelegramClient:
    @classmethod
    def send_message(cls, chat_id, text, reply_markup=None):
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", None) or getattr(settings, "TELEGRAM_TOKEN", None)
        if not token:
            logger.warning("TELEGRAM_BOT_TOKEN is not set.")
            return
        payload = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json=payload,
                timeout=10,
            )
            data = resp.json()
            if not data.get("ok"):
                logger.error(f"Telegram sendMessage failed for chat {chat_id}: {data}")
        except Exception as e:
            logger.warning(f"Failed to send telegram message to {chat_id}: {e}")


class TgOtpService:
    @classmethod
    def request(cls):
        config = SiteConfig.get_config()
        otp_mode = bool(config.send_otp_code)

        token = secrets.token_urlsafe(32)
        ttl = getattr(settings, "TELEGRAM_LOGIN_TOKEN_TTL_MINUTES", 5)
        expires_at = timezone.now() + timedelta(minutes=ttl)
        TelegramRepo.create_token(token, otp_mode, expires_at)
        bot_username = getattr(settings, "TELEGRAM_BOT_USERNAME", "")
        return {
            "token": token,
            "deep_link": f"https://t.me/{bot_username}?start={token}",
            "poll": not otp_mode,
        }

    @classmethod
    def _handle_start(cls, chat_id, telegram_id, frm, text):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            TelegramClient.send_message(
                chat_id, cls._no_token_msg(), reply_markup=REMOVE_KEYBOARD
            )
            return
        token_str = parts[1].strip()

        row = TelegramRepo.get_token(token_str)
        if not row:
            return
        if not cls._is_usable(row):
            TelegramClient.send_message(chat_id, EXPIRED_MSG)
            return

        TelegramRepo.set_telegram_id(row, telegram_id)

        if row.otp_mode:
            user = UserRepo.get_user_by_telegram_id(telegram_id)
            if not user:
                TelegramRepo.set_telegram_id(row, telegram_id)
                TelegramClient.send_message(
                    chat_id, ASK_PHONE_MSG, reply_markup=CONTACT_KEYBOARD
                )
                return
            TelegramRepo.set_user(row, user)
            sent, result = SmsService.create_otp_for_user(user)
            if sent:
                TelegramClient.send_message(chat_id, cls._otp_msg(result), reply_markup=REMOVE_KEYBOARD)
            else:
                TelegramClient.send_message(
                    chat_id, OTP_TIME_LIMIT_MSG.format(seconds=result), reply_markup=REMOVE_KEYBOARD
                )
            return

        user = UserRepo.get_user_by_telegram_id(telegram_id)
        if user:
            if not user.is_verified or not user.is_active:
                user.is_verified = True
                user.is_active = True
                user.save(update_fields=["is_verified", "is_active"])
            TelegramRepo.confirm(row, user)
            TelegramClient.send_message(
                chat_id, cls._success_msg(), reply_markup=REMOVE_KEYBOARD
            )
        else:
            TelegramClient.send_message(
                chat_id, ASK_PHONE_MSG, reply_markup=CONTACT_KEYBOARD
            )

    @classmethod
    def poll(cls, token_str):
        row = TelegramRepo.get_token(token_str)
        if not row:
            return {"error": "invalid"}

        if row.status == "CONFIRMED" and row.user_id:
            user = row.user
            if user is None:
                return {"error": "invalid"}
            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken.for_user(user)
            TelegramRepo.expire(row)
            return {
                "status": "CONFIRMED",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }

        if row.status == "EXPIRED" or timezone.now() > row.expires_at:
            if row.status == "PENDING":
                TelegramRepo.expire(row)
            return {"error": "expired"}

        return {"status": "PENDING"}

    @classmethod
    def verify_otp(cls, token_str, code):
        row = TelegramRepo.get_token(token_str)
        if not cls._is_usable(row):
            return {"error": "expired"}
        if not row.user_id:
            return {"error": "invalid"}

        user = row.user
        config = SiteConfig.get_config()
        timeout_seconds = config.otp_timeout_seconds or 300
        cutoff = timezone.now() - timedelta(seconds=timeout_seconds)

        otp = None
        try:
            code_int = int(code)
            candidate = (
                UserAuthOtp.objects.filter(
                    user=user,
                    code=code_int,
                    is_used=False,
                )
                .order_by("-id")
                .first()
            )
            if candidate and candidate.otp_created_at:
                otp_time = candidate.otp_created_at
                if timezone.is_naive(otp_time):
                    otp_time = timezone.make_aware(otp_time)
                if otp_time >= cutoff:
                    otp = candidate
        except (ValueError, TypeError):
            pass

        otp_valid = False
        if otp:
            otp_valid = True
        elif user.otp and user.otp == str(code):
            user_otp_time = user.otp_created_at
            if user_otp_time:
                if timezone.is_naive(user_otp_time):
                    user_otp_time = timezone.make_aware(user_otp_time)
                if user_otp_time >= cutoff:
                    otp_valid = True

        if not otp_valid:
            return {"error": "invalid_otp"}

        if otp:
            otp.is_used = True
            otp.verified = True
            otp.save(update_fields=["is_used", "verified"])

        if not user.is_verified or not user.is_active:
            user.is_verified = True
            user.is_active = True
            user.save(update_fields=["is_verified", "is_active"])

        TelegramRepo.confirm(row, user)

        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(row.user)
        return {
            "status": "CONFIRMED",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @classmethod
    def _handle_contact(cls, chat_id, telegram_id, frm, contact):
        logger.info(f"contact: {contact}")
        contact_user_id = contact.get("user_id")
        if contact_user_id is not None and str(contact_user_id) != str(telegram_id):
            TelegramClient.send_message(chat_id, WRONG_CONTACT_MSG)
            return

        row = TelegramRepo.get_pending_token_by_telegram_id(telegram_id)
        if not row:
            return
        if not cls._is_usable(row):
            TelegramClient.send_message(
                chat_id, EXPIRED_MSG, reply_markup=REMOVE_KEYBOARD
            )
            return

        phone = cls._normalize_phone(contact.get("phone_number") or "")
        user = cls._link_or_create_user(phone, telegram_id, frm)

        if row.otp_mode:
            TelegramRepo.set_user(row, user)
            sent, result = SmsService.create_otp_for_user(user)
            if not sent:
                TelegramClient.send_message(
                    chat_id, OTP_TIME_LIMIT_MSG.format(seconds=result), reply_markup=REMOVE_KEYBOARD
                )
                return
            TelegramClient.send_message(chat_id, cls._otp_msg(result), reply_markup=REMOVE_KEYBOARD)
        else:
            user.is_verified = True
            user.is_active = True
            user.save(update_fields=["is_verified", "is_active"])
            TelegramRepo.confirm(row, user)
            TelegramClient.send_message(
                chat_id, cls._success_msg(), reply_markup=REMOVE_KEYBOARD
            )

    @classmethod
    def handle_update(cls, update):
        if "callback_query" in update:
            cb = update["callback_query"]
            cb_id = cb.get("id")
            token = getattr(settings, "TELEGRAM_BOT_TOKEN", None) or getattr(settings, "TELEGRAM_TOKEN", None)
            if token and cb_id:
                try:
                    requests.post(
                        f"https://api.telegram.org/bot{token}/answerCallbackQuery",
                        json={"callback_query_id": cb_id},
                        timeout=5,
                    )
                except Exception:
                    pass
            return

        message = update.get("message") or {}
        frm = message.get("from") or {}
        telegram_id = frm.get("id")
        if not telegram_id:
            return

        chat_id = (message.get("chat") or {}).get("id") or telegram_id
        contact = message.get("contact")

        if contact:
            cls._handle_contact(chat_id, telegram_id, frm, contact)
            return

        text = message.get("text") or ""
        if text.startswith("/start"):
            cls._handle_start(chat_id, telegram_id, frm, text)

    @staticmethod
    def _success_msg():
        url = getattr(settings, "TELEGRAM_LOGIN_RETURN_URL", "")
        return SUCCESS_MSG_WITH_URL.format(url=url) if url else SUCCESS_MSG

    @staticmethod
    def _otp_msg(otp):
        return f"Ilovaga kirish uchun OTP kodingiz: {otp}"

    @staticmethod
    def _no_token_msg():
        url = getattr(settings, "TELEGRAM_LOGIN_RETURN_URL", "")
        return NO_TOKEN_MSG_WITH_URL.format(url=url) if url else NO_TOKEN_MSG

    @staticmethod
    def _is_usable(row):
        return (
            bool(row) and row.status == "PENDING" and timezone.now() <= row.expires_at
        )

    @staticmethod
    def _normalize_phone(raw):
        digits = "".join(ch for ch in raw if ch.isdigit())
        if len(digits) == 9:
            digits = "998" + digits
        return digits

    @classmethod
    def _link_or_create_user(cls, phone, telegram_id, frm):
        user = None
        if phone:
            user = UserRepo.get_user_by_username(phone)
        if not user:
            user = UserRepo.create_telegram_user(
                username=phone or f"tg_{telegram_id}",
                first_name=frm.get("first_name") or "",
                last_name=frm.get("last_name") or "",
                phone=phone,
            )
        UserRepo.attach_telegram(user, telegram_id, frm.get("username") or "")
        return user
