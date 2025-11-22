from django.contrib.auth.models import BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(email, password, **extra_fields)

        return user

# class CustomUserManager(BaseUserManager):
#     def create_user(self, phone_number=None, email=None,password = None ,**extra_fields):
#         if not username:
#             raise ValueError('Phone_number maydoni bo`lishi kerak emas!')
#         # phone_number = self.normalize_phone_number(phone_number)
#         user = self.model(phone_number=phone_number, email=email, **extra_fields)
        
#         user.set_password(password or '123456')
#         user.save(using=self._db)
#         return user


#     def create_superuser(self, username, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         extra_fields.setdefault("is_active", True)

#         if extra_fields.get("is_staff") is not True:
#             raise ValueError("Superuser must have is_staff=True.")
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser=True.")

#         user = self.create_user(username, password, **extra_fields)

#         # superuser uchun default ADMIN roli berish
#         from apps.users.models import UserRole
#         UserRole.objects.get_or_create(user=user, role="ADMIN")

#         return user
