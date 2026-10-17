from django.urls import path

from apps.notification.api.views.notification_list import NotificationListView
from apps.notification.api.views.notification_read import NotificationReadView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification_list"),
    path("read/", NotificationReadView.as_view(), name="notification_read"),
]
