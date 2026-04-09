from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView)


urlpatterns = [

    path('api/admin/', admin.site.urls),
    path('api/user/', include('apps.users.urls')),
    path('api/post/', include('apps.posts.urls')),
    path('api/shared/', include('apps.shared.urls')),
    path("api/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="schema-swagger-ui"),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

