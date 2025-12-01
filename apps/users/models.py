from django.db import models
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import MyUserManager

# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True,null=True)
    updated_at = models.DateField(auto_now=True,null=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel, PermissionsMixin):
    LANG_CHOICES = (
        ('EN', 'EN'),
        ('RU', 'RU'),
        ('UZ', 'UZ')
    )
    phone_regex = RegexValidator(
        regex=r'^998\d{9}$',
        message="Telefon raqam '998XXXXXXXXX' formatida bo'lishi kerak!"
    )

    first_name = models.CharField(max_length=255,null=True)
    last_name = models.CharField(max_length=255,null=True)
    email = models.EmailField(unique=True, default=None)
    phone_number = models.CharField(max_length=12, blank=True, null=True, validators=[phone_regex], verbose_name=_('phone_number'))
    image = models.ImageField(upload_to='user/images', blank=True, null=True, verbose_name=_('image'), default='user/user_default.jpeg')
    language = models.CharField(choices=LANG_CHOICES, max_length=2, default='UZ', verbose_name=_('lang'))
    password = models.CharField(max_length=255,null=True, verbose_name=_('password'))
    lat = models.FloatField(null=True, blank=True, verbose_name=_("lat"))
    longitude = models.FloatField(null=True, blank=True, verbose_name=_("long"))
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("age"))
    is_active = models.BooleanField(default=False, verbose_name=_('is_active'))
    is_verified = models.BooleanField(default=False, verbose_name=_('is_verified'))
    otp = models.CharField(max_length=4, null=True, verbose_name=_("otp"))
    otp_created_at = models.DateTimeField(null=True, verbose_name=_('otp_created_at'))
    region = models.ForeignKey('shared.Region', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("region"))
    district = models.ForeignKey('shared.District', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("district"))

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or self.phone_number or f"{self.id}"



class UserAuthOtp(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    # user = models.ForeignKey(User, verbose_name=_('userotp'), on_delete=models.CASCADE)
    code = models.IntegerField()
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_used = models.BooleanField(default=False)
    incorrect_count = models.IntegerField(default=0)
    verified = models.BooleanField(default=False, verbose_name=_('verified'))


class VersionControl(BaseModel):
    DEVICE_TYPE_CHOICES = (
        ("IOS", "IOS"),
        ("ANDROID", "ANDROID")
    )
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES, verbose_name=_("device_type"))
    current_version = models.CharField(max_length=10, verbose_name=_("current_version"))
    is_active = models.BooleanField(default=False, verbose_name=_("is_active"))
    force_update = models.BooleanField(default=False, verbose_name=_("force_update"))

    def __str__(self):
        return f"{self.device_type} - {self.current_version}"

    class Meta:
        verbose_name = _("App Version Control")
        verbose_name_plural = _("App Version Controls")
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
    email = models.CharField(max_length=12, verbose_name=_("email"), blank=True, null=True)
    message_id = models.CharField(max_length=17, verbose_name=_("message_id"))
    otp = models.CharField(max_length=4, null=True, blank=True, verbose_name=_("otp"))

    class Meta:
        indexes = [
            # CRITICAL: Used for rate limiting - count OTPs sent today per phone
            models.Index(fields=['email', 'created_at'], name='otp_log_email_created_idx'),
        ]

class UserPasswordReset(BaseModel):
    user = models.OneToOneField(User, models.CASCADE, blank=True, null=True)  # OneToOneField auto-creates unique index
    reset_token = models.UUIDField(editable=True, null=True, blank=True, unique=True)  # unique=True auto-creates index
    reset_token_created_at = models.DateTimeField(null=True, blank=True)
    code = models.CharField(max_length=4, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    incorrect_count = models.IntegerField(default=0)
    otp_count = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
