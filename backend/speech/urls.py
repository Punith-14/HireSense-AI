from django.urls import path

from speech import views


urlpatterns = [
    path("transcribe/", views.transcribe, name="speech_transcribe"),
]
