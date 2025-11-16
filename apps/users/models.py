from django.db import models
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.utils.translation import gettext_lazy as _


# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True,null=True)
    updated_at = models.DateField(auto_now=True,null=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, email=None,password = None ,**extra_fields):
        if not phone_number:
            raise ValueError('Phone_number maydoni bo`lishi kerak emas!')
        # phone_number = self.normalize_phone_number(phone_number)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        
        user.set_password(password or '123456')
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, email=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser is_admin=True bo`lishi kerak!')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True bo`lishi kerak!')

        return self.create_user(phone_number, email, password, **extra_fields)


class User(AbstractUser, BaseModel, PermissionsMixin):
    LANG_CHOICES = (
        ('EN', 'EN'),
        ('RU', 'RU'),
        ('UZ', 'UZ')
    )
    # phone_regex = RegexValidator(
    #     regex=r'^\+998\d{9}$',
    #     message="Telefon raqam '+998XXXXXXXXX' formatida bo'lishi kerak!"
    # )
    name = models.CharField(max_length=255,null=True)
    email = models.EmailField(unique=True, default=None,blank=True,null=True)
    phone_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    language = models.CharField(choices=LANG_CHOICES, max_length=2, default='UZ', verbose_name=_('lang'))

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username if self.username else self.email

    # @property
    # def is_superuser(self):
    #     return self.is_admin


class UserRole(BaseModel):
    ROLE_CHOICES = (
        ('ADMIN', 'ADMIN'),
        ('SELLER', 'SELLER'),
        ('USER', 'USER')
    )
    user = models.ForeignKey(User, verbose_name=("userrole"), on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name=("role"))
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    password = models.CharField(max_length=255, verbose_name=_('password'))
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        unique_together=('user', 'role')


class UserAuthOtp(BaseModel):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=("userotp"), on_delete=models.CASCADE)
    otp = models.IntegerField()
    is_used = models.BooleanField(default=False)
    incorrect_count = models.IntegerField(default=0)
    verified = models.BooleanField(default=False, verbose_name=("verified"))


class VersionControl(BaseModel):
    DEVICE_TYPE_CHOICES = (
        ("IOS", "IOS"),
        ("ANDROID", "ANDROID")
    )
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES, verbose_name=("device_type"))
    current_version = models.CharField(max_length=10, verbose_name=("current_version"))
    is_active = models.BooleanField(default=False, verbose_name=("is_active"))
    force_update = models.BooleanField(default=False, verbose_name=("force_update"))

    def __str__(self):
        return f"{self.device_type} - {self.current_version}"

    class Meta:
        verbose_name = ("App Version Control")
        verbose_name_plural = ("App Version Controls")
        db_table = "app_version_control"


class UserDevice(BaseModel):
    DEVICE_TYPE_CHOICES = (
        ("IOS", "IOS"),
        ("ANDROID", "ANDROID")
    )

    user = models.ForeignKey(User, models.CASCADE, "user_devices", verbose_name=_("user"))
    role = models.CharField(max_length=20, verbose_name=_("role"))
    device_id = models.CharField(max_length=50, verbose_name=_("device_id"))
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES, verbose_name=_("device_type"))

    class Meta:
        unique_together = ('user', 'device_id', 'role')


class OtpSentLog(BaseModel):
    email = models.CharField(max_length=12)
    message_id = models.CharField(max_length=17)
    otp = models.CharField(max_length=4, null=True, blank=True)
