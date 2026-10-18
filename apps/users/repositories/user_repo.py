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
        if user.email and user.email.endswith("@telegram.user"):
            user.email = None
            user.save(update_fields=["telegram_id", "telegram_username", "email"])
        else:
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
            uname = phone or username
            user = User.objects.create(
                username=uname,
                email=None,
                phone_number=phone or (uname if uname and uname.startswith("998") else None),
                full_name=full_name,
                is_active=True,
                is_verified=True,
            )
            user.set_unusable_password()
            user.save()
        else:
            if user.email and user.email.endswith("@telegram.user"):
                user.email = None
                user.save(update_fields=["email"])
        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return User.objects.filter(id=user_id).first()
