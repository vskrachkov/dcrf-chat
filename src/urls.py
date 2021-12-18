from django.contrib import admin
from django.urls import include, path
from drf_info_endpoint.views import info
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from dcrf_docs.views import async_docs
from version import __version__

admin.site.site_header = f"dcrf-chat {__version__}"
admin.site.site_title = "dcrf-chat"
admin.site.index_title = "dcrf-chat"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("info/", info),
    path("async_api_docs/", async_docs),
    path("health/", include("drf_health_check.urls")),
    path("", include("chat.urls", namespace="chat")),
]
