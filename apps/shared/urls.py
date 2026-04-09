from django.urls import path
from .views import SharedView

urlpatterns = [
    path('regions/', SharedView.as_view(), name='shared-view'),
]