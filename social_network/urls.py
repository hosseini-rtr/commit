from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    # MVT URLs (existing templates)
    path("", include("posts.urls")),
    path("", include("users.urls")),
    path("", include("interactions.urls")),
    path("", include("social.urls")),
    # DRF API URLs
    path("api/", include("posts.api_urls")),
    path("api/users/", include("users.api_urls")),
    path("api/social/", include("social.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
