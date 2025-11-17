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
    # phone_regex = RegexValidator(
    #     regex=r'^\+998\d{9}$',
    #     message="Telefon raqam '+998XXXXXXXXX' formatida bo'lishi kerak!"
    # )
    name = models.CharField(max_length=255,null=True)
    email = models.EmailField(unique=True, default=None,blank=True,null=True)
    image = models.ImageField(upload_to='user/images', blank=True, null=True, verbose_name=_('image'))
    phone_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
    language = models.CharField(choices=LANG_CHOICES, max_length=2, default='UZ', verbose_name=_('lang'))

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
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
    user = models.ForeignKey(User, verbose_name=_('userrole'), on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name=_('role'))
    lat = models.FloatField(null=True, blank=True, verbose_name=_('lat'))
    long = models.FloatField(null=True, blank=True, verbose_name=_('long'))
    password = models.CharField(max_length=255,null=True, verbose_name=_('password'))
    is_verified = models.BooleanField(default=False, verbose_name=_('is_verified'))
    is_active = models.BooleanField(default=False, verbose_name=_('is_active'))
    otp = models.CharField(max_length=4, null=True, verbose_name=_("otp"))
    otp_created_at = models.DateTimeField(null=True, verbose_name=_('otp_created_at'))

    class Meta:
        unique_together=('user', 'role')


class UserAuthOtp(BaseModel):
    user_role = models.OneToOneField(UserRole, on_delete=models.CASCADE)
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
    email = models.CharField(max_length=12, verbose_name=_("email"))
    message_id = models.CharField(max_length=17, verbose_name=_("message_id"))
    otp = models.CharField(max_length=4, null=True, blank=True, verbose_name=_("otp"))


class UserPasswordReset(BaseModel):
    user_role = models.OneToOneField(UserRole, models.CASCADE)  # OneToOneField auto-creates unique index
    reset_token = models.UUIDField(editable=True, null=True, blank=True, unique=True)  # unique=True auto-creates index
    reset_token_created_at = models.DateTimeField(null=True, blank=True)
    code = models.CharField(max_length=4, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    incorrect_count = models.IntegerField(default=0)
    otp_count = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)


class OtpSentLog(BaseModel):
    email = models.CharField(null=True,max_length=12)
    message_id = models.CharField(max_length=17)
    otp = models.CharField(max_length=4, null=True, blank=True)

    class Meta:
        indexes = [
            # CRITICAL: Used for rate limiting - count OTPs sent today per phone
            models.Index(fields=['email', 'created_at'], name='otp_log_email_created_idx'),
        ]
