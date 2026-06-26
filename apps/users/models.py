from django.db import models
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import MyUserManager


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True,null=True)
    updated_at = models.DateField(auto_now=True,null=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel, PermissionsMixin):
    phone_regex = RegexValidator(
        regex=r'^998\d{9}$',
        message="Telefon raqam '998XXXXXXXXX' formatida bo'lishi kerak!"
    )
    username = models.CharField(blank=True, max_length=255, verbose_name=_('username'), null=True)
    full_name = models.CharField(max_length=255,null=True, blank=True, verbose_name=_('full_name'))
    email = models.EmailField(unique=True, default=None)
    phone_number = models.CharField(max_length=12, blank=True, null=True, validators=[phone_regex], verbose_name=_('phone_number'))
    image = models.ImageField(upload_to='user/images', blank=True, null=True, verbose_name=_('image'), default='user/user_default.jpeg')
    age = models.IntegerField(blank=True, null=True, verbose_name=_('age'))
    password = models.CharField(max_length=255,null=True, verbose_name=_('password'))
    is_active = models.BooleanField(default=False, verbose_name=_('is_active'))
    is_verified = models.BooleanField(default=False, verbose_name=_('is_verified'))
    otp = models.CharField(max_length=4, null=True, verbose_name=_("otp"))
    otp_created_at = models.DateTimeField(null=True, verbose_name=_('otp_created_at'))

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or self.phone_number or f"{self.id}"


class UserAuthOtp(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    code = models.IntegerField()
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_used = models.BooleanField(default=False)
    incorrect_count = models.IntegerField(default=0)
    verified = models.BooleanField(default=False, verbose_name=_('verified'))


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
