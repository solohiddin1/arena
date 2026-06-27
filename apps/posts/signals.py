from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.posts.models import AppFeedback, AdminNotification


@receiver(post_save, sender=AppFeedback)
def create_admin_notification_on_feedback(sender, instance, created, **kwargs):
    if created:
        user_info = instance.user.email if instance.user else "Anonymous"
        rating_info = f"{instance.rating}/5" if instance.rating else "no rating"
        AdminNotification.objects.create(
            type='APP_FEEDBACK',
            message=f"New feedback from {user_info} ({rating_info}): {instance.message[:200]}",
            object_id=instance.id,
        )