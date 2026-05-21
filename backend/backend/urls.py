"""
URL configuration for hiresense_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView
from backend import admin_views


def health_check(request):
    return JsonResponse({"status": "ok", "service": "HireSenseAI backend"})


urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False), name='home'),
    path('health/', health_check, name='health_check'),
    path('api/interview/', include('interview.urls')),
    path('api/speech/', include('speech.urls')),
    path('api/vision/', include('vision.urls')),
    path('admin/hiresense/users/', admin_views.users_admin, name='hiresense_admin_users'),
    path('admin/hiresense/sessions/', admin_views.sessions_admin, name='hiresense_admin_sessions'),
    path('admin/hiresense/interviews/', admin_views.interviews_admin, name='hiresense_admin_interviews'),
    path('admin/hiresense/reports/', admin_views.reports_admin, name='hiresense_admin_reports'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
