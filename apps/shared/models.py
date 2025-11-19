import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.


logger = logging.getLogger('myapp')


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
