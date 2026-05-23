from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/interview/', include('interview.urls')),
    path('api/speech/', include('speech.urls')),
    path('api/vision/', include('vision.urls')),
    path('api/users/', include('users.urls')),
]