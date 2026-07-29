from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView)


urlpatterns = [

    path('api/v1/admin/', admin.site.urls),
    path('api/v1/user/', include('apps.users.urls')),
    path('api/v1/post/', include('apps.posts.urls')),
    path('api/v1/shared/', include('apps.shared.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path("api/v1/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="schema-swagger-ui"),
        path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

