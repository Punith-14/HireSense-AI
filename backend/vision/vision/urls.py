from django.urls import path

from vision import views


urlpatterns = [
    path("analyze/", views.analyze_frame, name="vision_analyze"),
]
