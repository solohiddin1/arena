from django.db import models
from django.core.validators import RegexValidator
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
    full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('full_name'))
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True, validators=[phone_regex], verbose_name=_('phone_number'))
    telegram_id = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name=_('telegram_id'))
    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('telegram_username'))
    image = models.ImageField(upload_to='user/images', blank=True, null=True, verbose_name=_('image'), default='user/user_default.jpeg')
    age = models.IntegerField(blank=True, null=True, verbose_name=_('age'))
    password = models.CharField(max_length=255, null=True, verbose_name=_('password'))
    is_active = models.BooleanField(default=True, verbose_name=_('is_active'))
    is_verified = models.BooleanField(default=False, verbose_name=_('is_verified'))
    otp = models.CharField(max_length=4, null=True, blank=True, verbose_name=_("otp"))
    otp_created_at = models.DateTimeField(null=True, blank=True, verbose_name=_('otp_created_at'))

    email = None
    first_name = None
    last_name = None
    groups = None
    user_permissions = None

    objects = MyUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.phone_number:
            clean = str(self.phone_number).strip().replace("+", "").replace(" ", "").replace("-", "")
            self.phone_number = clean
            if not self.username:
                self.username = clean
        elif self.username:
            clean = str(self.username).strip().replace("+", "").replace(" ", "").replace("-", "")
            self.username = clean
            if not self.phone_number:
                self.phone_number = clean
        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone_number or self.username or self.full_name or f"User #{self.id}"


class UserAuthOtp(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    code = models.IntegerField()
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_used = models.BooleanField(default=False)
    incorrect_count = models.IntegerField(default=0)
    verified = models.BooleanField(default=False, verbose_name=_('verified'))


class TelegramLoginToken(BaseModel):
    STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("CONFIRMED", "CONFIRMED"),
        ("EXPIRED", "EXPIRED"),
    )

    token = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PENDING")
    telegram_id = models.BigIntegerField(null=True, blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tg_login_tokens",
    )
    expires_at = models.DateTimeField()
    otp_mode = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.token[:8]} {self.status}"


class Device(BaseModel):
    DEVICE_TYPE_CHOICES = (
        ("ANDROID", "ANDROID"),
        ("IOS", "IOS"),
        ("WEB", "WEB"),
    )
    name = models.CharField(max_length=128)
    device_type = models.CharField(
        max_length=16, choices=DEVICE_TYPE_CHOICES, default="WEB"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_device",
    )
    device_id = models.CharField(max_length=128)
    fcm_token = models.CharField(max_length=256, blank=True, default="")
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.device_type}) - {self.user_id}"
