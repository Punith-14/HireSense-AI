from django.urls import path

from interview import views


urlpatterns = [
    path("start/", views.start_interview, name="interview_start"),
    path("answer/", views.submit_answer, name="interview_answer"),
    path("evaluate/", views.evaluate_answer, name="interview_evaluate"),
    path("report/", views.interview_report, name="interview_report"),
]
