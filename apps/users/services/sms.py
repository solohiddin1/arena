import random
from datetime import timedelta

from django.utils import timezone

from apps.shared.models import SiteConfig
from apps.users.models import User, UserAuthOtp
from apps.users.repository import create_user_auth_otp_log, update_user_otp


class SmsService:
    @staticmethod
    def generate_otp() -> int:
        return random.randint(1000, 9999)

    @staticmethod
    def create_otp_for_user(user: User) -> tuple[bool, int]:
        allowed, seconds = SmsService.check_otp_generation(user)
        if not allowed:
            return False, seconds
        code = SmsService.generate_otp()
        now = timezone.now()
        update_user_otp(user.id, str(code), now)
        create_user_auth_otp_log(user=user, code=code, otp_created_at=now)
        return True, code

    @staticmethod
    def check_otp_generation(user: User) -> tuple[bool, int]:
        if getattr(user, "is_developer", False) or getattr(user, "is_superuser", False):
            return True, 0

        latest_otp = UserAuthOtp.objects.filter(user=user).order_by("-otp_created_at").first()
        if not latest_otp or not latest_otp.otp_created_at:
            return True, 0

        config = SiteConfig.objects.first()
        cooldown_seconds = config.otp_wait_seconds if config and config.otp_wait_seconds else 60
        cooldown = timedelta(seconds=cooldown_seconds)

        elapsed = timezone.now() - latest_otp.otp_created_at
        if elapsed > cooldown:
            return True, 0
        remaining = cooldown - elapsed
        return False, max(1, int(remaining.total_seconds()))
