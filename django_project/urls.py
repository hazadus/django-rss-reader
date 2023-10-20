"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("feeds/", include("feeds.urls")),
        path("__debug__/", include("debug_toolbar.urls")),
        path("accounts/", include("allauth.urls")),
        path("", include("core.urls")),
        path("users/", include("users.urls")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

# Configure Admin panel titles
admin.site.site_header = "RSS Reader Administration"
admin.site.site_title = "RSS Reader Admin"
admin.site.index_title = "RSS Reader Admin"
