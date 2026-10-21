from apps.users.models import User, BaseModel
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class AdminNotification(BaseModel):
    TYPES = (
        ('APP_FEEDBACK', 'App Feedback'),
    )
    type = models.CharField(max_length=50, choices=TYPES, default='APP_FEEDBACK')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    object_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Admin Notification"
        verbose_name_plural = "Admin Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{'READ' if self.is_read else 'NEW'}] {self.type} - {self.created_at}"


class AppFeedback(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='app_feedbacks', blank=True, null=True)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "App Feedback"
        verbose_name_plural = "App Feedbacks"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email if self.user else 'Anonymous'} - {self.rating or 'No rating'}"


class Favourite(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_favourites')
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name='post_favourites')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_favourite_user_post')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.post.title}"


class Feedback(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_feedbacks')
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name='post_feedbacks')
    rating = models.PositiveSmallIntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_feedback_user_post'),
            models.CheckConstraint(
                check=Q(rating__isnull=False) | Q(comment__isnull=False),
                name='feedback_has_rating_or_comment',
            ),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.post.title}"

class Amenity(BaseModel):
    title = models.CharField(max_length=100, verbose_name=_("title"), blank=True, null=True)
    is_positive = models.BooleanField(default=True, verbose_name=_("is positive"))
    is_main = models.BooleanField(default=False, db_index=True, verbose_name=_("is main"))
    category = models.ForeignKey("Category", on_delete=models.SET_NULL,
                                 related_name='category_amenities', blank=True, null=True)

    class Meta:
        verbose_name = _("Amenity")
        verbose_name_plural = _("Amenities")

    @property
    def main(self) -> bool:
        return self.is_main

    def __str__(self):
        return self.title or f"Amenity #{self.pk}"


class Post(BaseModel):
    post_states = (
        ('ACCEPTED', 'ACCEPTED'),
        ('CANCELLED', 'CANCELLED'),
        ('CHECKING', 'CHECKING'),
        ('FROZEN', 'FROZEN'),
    )
    title = models.CharField(max_length=100, verbose_name="Post title", null=True)
    location_title = models.CharField(max_length=255, verbose_name="Location title", blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user_posts', blank=True, null=True)
    lat = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    long = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    comment_count = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False, db_index=True)
    prices = models.JSONField(default=list, blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Post description")

    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone number")
    social_media_link = models.URLField(blank=True, null=True, verbose_name="Social media link")
    social_media_type = models.CharField(
        max_length=20,
        choices=(
            ('TELEGRAM', 'TELEGRAM'),
            ('INSTAGRAM', 'INSTAGRAM'),
            ('WHATSAPP', 'WHATSAPP'),
            ('FACEBOOK', 'FACEBOOK'),
            ('OTHER', 'OTHER'),
        ),
        blank=True,
        null=True,
        verbose_name="Social media type"
    )

    state = models.CharField(max_length=50, choices=post_states, default='CHECKING', verbose_name="Post state")
    region = models.ForeignKey("shared.Region", on_delete=models.SET_NULL, related_name='region_posts', blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, related_name='category_posts', blank=True, null=True)
    district = models.ForeignKey("shared.District", on_delete=models.SET_NULL, related_name='district_posts', blank=True, null=True)
    amenities = models.ManyToManyField("Amenity", related_name='posts', blank=True)

    def __str__(self):
        return self.title or f"Post #{self.pk}"

    @property
    def average_rating(self):
        return self.post_feedbacks.filter(rating__isnull=False).aggregate(avg=models.Avg('rating'))['avg']

    @property
    def total_feedbacks(self):
        return self.post_feedbacks.count()


class PostImage(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_images')
    image = models.ImageField(upload_to='post_images/')
    image_compressed = models.ImageField(upload_to='post_images_compressed/', blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        title = self.post.title if (self.post and self.post.title) else f"Post #{self.post_id}"
        return f"Image for {title}"


class PostCertificate(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_certificates')
    image = models.ImageField(upload_to='post_certificates/')
    image_compressed = models.ImageField(upload_to='post_certificates_compressed/', blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        title = self.post.title if (self.post and self.post.title) else f"Post #{self.post_id}"
        return f"Certificate for {title}"


class Category(BaseModel):
    title = models.CharField(max_length=255, verbose_name="Category title", null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    ordering = models.PositiveIntegerField(default=0, blank=True, null=True, db_index=True, verbose_name=_("Ordering"))

    class Meta:
        ordering = ['ordering', 'id']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def save(self, *args, **kwargs):
        is_new = self._state.adding or self.pk is None
        super().save(*args, **kwargs)
        if self.ordering is None or (is_new and self.ordering == 0):
            self.ordering = self.pk
            super().save(update_fields=['ordering'])

    def __str__(self):
        title = self.title or getattr(self, "title_uz", None) or getattr(self, "title_ru", None) or getattr(self, "title_en", None)
        return str(title or f"Category #{self.pk}")

class PostWorkDays(BaseModel):
    DAYS_OF_WEEK = [
        ('MONDAY', _('MONDAY')),
        ('TUESDAY', _('TUESDAY')),
        ('WEDNESDAY', _('WEDNESDAY')),
        ('THURSDAY', _('THURSDAY')),
        ('FRIDAY', _('FRIDAY')),
        ('SATURDAY', _('SATURDAY')),
        ('SUNDAY', _('SUNDAY')),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='work_days')
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
        default=False,
        verbose_name=_("is closed"),
        help_text=_("Agar True bo'lsa, bu kun yopiq")
    )
    is_full_time = models.BooleanField(default=False, verbose_name=_("is full time"))

    class Meta:
        verbose_name = _("Business Work Hours")
        verbose_name_plural = _("Business Work Hours")
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        if self.is_closed:
            return f"{self.post.title} - {self.get_day_of_week_display()}: {_('Closed')}"
        return f"{self.post.title} - {self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"