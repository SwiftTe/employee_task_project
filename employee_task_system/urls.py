"""
URL configuration for employee_task_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from utils.health_checks import HealthCheckView, DetailedHealthView

urlpatterns = [
    # Redirect root URL to admin panel
    path('', RedirectView.as_view(url='/admin/')),
    
    # Admin panel
    path('admin/', admin.site.urls),

    # API endpoints (versioned)
    path('api/auth/', include('users.urls')),        # authentication & user management
    path('api/tasks/', include('tasks.urls')),       # task management
    path('api/analytics/', include('analytics.urls')),  # analytics

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Health check endpoints
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('health/detailed/', DetailedHealthView.as_view(), name='detailed-health'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

