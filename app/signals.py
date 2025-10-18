from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db.models.signals import m2m_changed


# @receiver(m2m_changed,sender=Group.students_set.through)
# def update_student_count(sender,instance,**kwargs):
#     instance.student_count = instance.students_set.count()
#     instance.save()


# @receiver(post_delete, sender = settings.AUTH_USER_MODEL)
# def delete_user_token(sender, instance, **kwargs):
#     try:
#         token = Token.objects.get(user=instance)
#         token.delete()
#         print(f"Token deleted successfully for user {instance}.")
#     except Token.DoesNotExist:
#         pass