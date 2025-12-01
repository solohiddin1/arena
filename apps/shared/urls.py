from django.urls import path
from .views import SharedView

urlpatterns = [
    path('shared/', SharedView.as_view(), name='shared-view'),
]