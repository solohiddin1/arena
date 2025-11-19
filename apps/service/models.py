from django.db import models
from apps.users.models import BaseModel
from django.utils.translation import gettext_lazy as _
from apps.shared.models import Region, District
from parler.models import TranslatableModel, TranslatedFields
from apps.users.models import User
from django.contrib.auth.models import AbstractUser, PermissionsMixin

# Create your models here.

class BusinessStatusEnum(models.TextChoices):
    CHECKING = "CHECKING", _('CHECKING')
    ACCEPTED = "ACCEPTED", _('ACCEPTED')
    CANCELLED = "CANCELLED", _('CANCELLED')


class Submission(models.Model):
    mxik_code = models.BigIntegerField(verbose_name=_("mxik_code"), null=True, blank=True)
    category_name = models.CharField(max_length=255, verbose_name=_("category_name"))
    description = models.CharField(max_length=500, verbose_name=_("description"))
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name=_("applied_at"))
    applied = models.BooleanField(default=False, verbose_name=_("applied"))
    parend = models.CharField(max_length=255, verbose_name=_("parend"))

    class Meta:
        verbose_name = _("Submission")
        verbose_name_plural = _("Submissions")

    def __str__(self):
        return self.category_name


# class UnitEnum(models.TextChoices):
#     SUM = "SUM", _('SUM')
#     PERCENT = "PERCENT", _('PERCENT')


# class Comission(models.Model):
#     name = models.CharField(max_length=255, verbose_name=_("name"))
#     unit = models.CharField(choices=UnitEnum.choices, default=UnitEnum.SUM, max_length=10, verbose_name=_("unit"),
#                             null=True, blank=True)
#     amount = models.BigIntegerField(null=True, verbose_name=_("amount"))

#     class Meta:
#         verbose_name = _("Comission")
#         verbose_name_plural = _("Comissions")

#     def __str__(self):
#         return self.name


class BusinessType(TranslatableModel, BaseModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_("name"), null=True, blank=True),
        hint_text=models.CharField(max_length=255, verbose_name=_("hint_text"), null=True, blank=True),
        title=models.CharField(max_length=255, verbose_name=_("titles"), null=True, blank=True)
    )
    # comission = models.ForeignKey(Comission, models.CASCADE, "business_types", verbose_name=_("comission"), null=True,blank=True)

    inn_lenth = models.BigIntegerField(null=True, blank=True, verbose_name=_("inn_lenth"))

    class Meta:
        verbose_name = _("Business Type")
        verbose_name_plural = _("Business Types")

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or str(self.id)


class BusinessCategory(TranslatableModel, BaseModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_("name")),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("is_active"))
    image = models.ImageField(null=True, blank=True, verbose_name=_("image"), upload_to='business/categories/')

    def __str__(self):
        return self.safe_translation_getter('name')

    class Meta:
        verbose_name = _("Business Category")
        verbose_name_plural = _("Business Categories")


class Service(BaseModel):
    user = models.ForeignKey(User, models.CASCADE, "services", verbose_name=_("user"))
    title = models.CharField(max_length=255, verbose_name=_("title"))  # language
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))
    image = models.ImageField(upload_to='services/', null=True, blank=True, verbose_name=_("image"))
    tin = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("tin"))
    business_category = models.ForeignKey(BusinessCategory, models.CASCADE, null=True, blank=True,
                                          verbose_name=_("business_category"))
    business_type = models.ForeignKey(BusinessType, models.CASCADE,
                                      verbose_name=_("business_type"))
    region = models.ForeignKey(Region, models.CASCADE, null=True, blank=True, verbose_name=_("region"))
    district = models.ForeignKey(District, models.CASCADE, null=True, blank=True, verbose_name=_("district"))
    address = models.CharField(max_length=500, verbose_name=_("address"))
    phone_number = models.CharField(max_length=12, verbose_name=_("phone_number"))
    lat = models.FloatField(null=True, blank=True, verbose_name=_("lat"))
    long = models.FloatField(null=True, blank=True, verbose_name=_("long"))
    state = models.CharField(choices=BusinessStatusEnum.choices, default=BusinessStatusEnum.CHECKING, max_length=10,
                             verbose_name=_("state"))
    is_active = models.BooleanField(default=True, verbose_name=_("is_active"))
    is_payment_cash = models.BooleanField(default=False, null=True, blank=True, verbose_name=_("is_payment_cash"))
    is_payment_card = models.BooleanField(default=False, null=True, blank=True, verbose_name=_("is_payment_card"))
    # categories = models.ManyToManyField('product.Category', blank=True, related_name='businesses', verbose_name=_("categories"))

    # AmoCRM Integration fields
    amocrm_lead_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("amocrm_lead_id"),
        help_text="AmoCRM Lead ID (biznes tasdiqlash uchun)"
    )
    amocrm_contact_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("amocrm_contact_id"),
        help_text="AmoCRM Contact ID (biznes egasi)"
    )

    class Meta:
        verbose_name = _("Business")
        verbose_name_plural = _("Businesses")

    def __str__(self):
        return self.title


# class DeliveredTime(BaseModel):
#     business = models.ForeignKey(Business, models.CASCADE, "delivered_times", verbose_name=_("business"))
#     from_time = models.TimeField(verbose_name=_("from_time"))
#     to_time = models.TimeField(verbose_name=_("to_time"))

#     class Meta:
#         verbose_name = _("Delivered Time")
#         verbose_name_plural = _("Delivered Times")


# class UserUsername(models.Model):
#     username = models.CharField(max_length=255, unique=True, primary_key=True)
#     used = models.BooleanField(default=False)


class StaffSeller(AbstractUser, PermissionsMixin, BaseModel):
    phone_number = models.CharField(max_length=255, verbose_name=_("phone_number"))
    avatar = models.ImageField(upload_to='seller/avatars/', null=True, verbose_name=_("avatar"))
    service = models.ForeignKey(Service, models.CASCADE, "sellers", verbose_name=_("service"))

    class Meta:
        verbose_name = _("Seller")
        verbose_name_plural = _("Sellers")

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='seller_set',
        blank=True,
        help_text='The groups this seller belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='seller_set',
        blank=True,
        help_text='Specific permissions for this seller.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username


class ServiceWorkDays(BaseModel):
    """Har bir vaqt oralig'ini alohida saqlaydigan model"""

    DAYS_OF_WEEK = [
        ('MONDAY', _('MONDAY')),
        ('TUESDAY', _('TUESDAY')),
        ('WEDNESDAY', _('WEDNESDAY')),
        ('THURSDAY', _('THURSDAY')),
        ('FRIDAY', _('FRIDAY')),
        ('SATURDAY', _('SATURDAY')),
        ('SUNDAY', _('SUNDAY')),
    ]

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='work_hours',
        verbose_name=_("business")
    )

    day_of_week = models.CharField(
        max_length=10,
        choices=DAYS_OF_WEEK,
        verbose_name=_("day of week")
    )

    start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("start time")
    )

    end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("end time")
    )

    is_closed = models.BooleanField(
        default=True,
        verbose_name=_("is closed"),
        help_text=_("Agar True bo'lsa, bu kun yopiq")
    )
    is_full_time = models.BooleanField(default=False, verbose_name=_("is full time"))

    class Meta:
        verbose_name = _("Business Work Hours")
        verbose_name_plural = _("Business Work Hours")
        ordering = ['day_of_week', 'start_time']
        db_table = 'business_work_hours'

    def __str__(self):
        if self.is_closed:
            return f"{self.business.title} - {self.get_day_of_week_display()}: {_('Closed')}"
        return f"{self.business.title} - {self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"


class ViewerTypeEnum(models.TextChoices):
    CLIENT = "CLIENT", _('CLIENT')
    SELLER = "SELLER", _('SELLER')
    ALL = "ALL", _('ALL')


class Banner(TranslatableModel, BaseModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=50, null=True, verbose_name=_("name")),  # language
        image=models.ImageField(upload_to='banners/', verbose_name=_("image"))  # language
    )
    link = models.URLField(null=True, blank=True, verbose_name=_("link"))
    is_active = models.BooleanField(default=False, verbose_name=_("is_active"))
    service = models.ForeignKey(Service, models.SET_NULL,
                                 "banners",
                                 null=True, blank=True,
                                 verbose_name=_("service"))
    viewer_type = models.CharField(choices=ViewerTypeEnum.choices,
                                   default=ViewerTypeEnum.CLIENT,
                                   max_length=10,
                                   verbose_name=_("viewer_type"))

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or str(self.id)


class ServiceWishlist(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_wishlists', verbose_name=_("user"))
    service = models.ForeignKey(Service, models.CASCADE, related_name="service_wishlists",
                                 verbose_name=_("service"))

    class Meta:
        unique_together = ('user', 'service')
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'


# class ServiceDeliveryRule(models.Model):
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="delivery_rules")
#     min_price = models.IntegerField()
#     max_price = models.IntegerField()
#     delivery_price = models.IntegerField()
