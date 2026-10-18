from django.db import models
from django.utils.translation import gettext_lazy as _


class Region(models.Model):
    soato_id = models.IntegerField(blank=True, null=True)
    name_uz = models.CharField(max_length=30, verbose_name=_("name_uz"), null=True, blank=True)
    name_ru = models.CharField(max_length=30, verbose_name=_("name_ru"), null=True, blank=True)
    name_en = models.CharField(max_length=30, verbose_name=_("name_en"), null=True, blank=True)

    def __str__(self):
        return self.name_uz or self.name_en or self.name_ru

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


class District(models.Model):
    soato_id = models.IntegerField(blank=True, null=True)
    name_uz = models.CharField(max_length=30, verbose_name=_("name_uz"), null=True, blank=True)
    name_ru = models.CharField(max_length=30, verbose_name=_("name_ru"), null=True, blank=True)
    name_en = models.CharField(max_length=30, verbose_name=_("name_en"), null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name=_("region"))

    def __str__(self):
        return self.name_ru or self.name_en or self.name_uz

    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("Districts")


class SiteConfig(models.Model):
    send_otp_code = models.BooleanField(
        default=False,
        verbose_name=_("Send OTP code via Telegram"),
        help_text=_("If checked, user receives OTP in Telegram. If unchecked, direct mobile polling login is enabled."),
    )
    otp_wait_seconds = models.IntegerField(
        default=60,
        verbose_name=_("OTP wait / cooldown (seconds)"),
        help_text=_("Time in seconds user must wait before requesting a new OTP."),
    )
    otp_timeout_seconds = models.IntegerField(
        default=300,
        verbose_name=_("OTP expiration timeout (seconds)"),
        help_text=_("Validity period of the OTP code in seconds."),
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = _("Site Config")
        verbose_name_plural = _("Site Configs")

    def __str__(self):
        return f"SiteConfig (send_otp_code={self.send_otp_code}, wait={self.otp_wait_seconds}s, timeout={self.otp_timeout_seconds}s)"

