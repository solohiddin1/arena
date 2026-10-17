from django.db.models import Q
from apps.users.models import User


class UserRepo:
    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        if not username:
            return None
        return User.objects.filter(
            Q(username=username) | Q(phone_number=username) | Q(email=username)
        ).first()

    @staticmethod
    def get_user_by_telegram_id(telegram_id) -> User | None:
        if not telegram_id:
            return None
        return User.objects.filter(telegram_id=str(telegram_id)).first()

    @classmethod
    def attach_telegram(cls, user: User, telegram_id, telegram_username: str = ""):
        user.telegram_id = str(telegram_id)
        if telegram_username:
            user.telegram_username = telegram_username
        user.save(update_fields=["telegram_id", "telegram_username"])
        return user

    @classmethod
    def create_telegram_user(
        cls, username: str, first_name: str = "", last_name: str = "", phone: str = ""
    ) -> User:
        user = None
        if phone:
            user = User.objects.filter(Q(phone_number=phone) | Q(username=phone)).first()
        if not user and username:
            user = User.objects.filter(username=username).first()

        if not user:
            full_name = f"{first_name} {last_name}".strip()
            # If user has no email, create unique placeholder email
            email_candidate = f"{username}@telegram.user" if "@" not in username else username
            if User.objects.filter(email=email_candidate).exists():
                email_candidate = f"{username}_{User.objects.count()}@telegram.user"

            user = User.objects.create(
                username=username,
                email=email_candidate,
                phone_number=phone or (username if username.startswith("998") else None),
                full_name=full_name,
                is_active=True,
                is_verified=True,
            )
            user.set_unusable_password()
            user.save()
        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return User.objects.filter(id=user_id).first()
