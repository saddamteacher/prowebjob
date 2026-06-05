"""Main URL configuration."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('vacancies/', include('vacancies.urls')),
    path('companies/', include('companies.urls')),
    path('platforms/', include('platforms.urls')),
    path('analytics/', include('analytics.urls')),
    path('parsers/', include('parsers.urls')),
    path('ai/', include('ai.urls')),
    path('settings/', include('settings_app.urls')),
    path('logs/', include('logs_app.urls')),
    path('scheduler/', include('scheduler.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
