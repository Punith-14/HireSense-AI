from django.urls import path

from .views import (
    generate_question,
    evaluate_response,
    start_interview,
    submit_answer,
    evaluate_answer,
    interview_report,
    interview_history,
    generate_hr_question,
    evaluate_hr_response,
    generate_behavioral_question,
    evaluate_behavioral_response
)

urlpatterns = [
    # Person 1 endpoints
    path('generate-question/', generate_question),
    path('evaluate-response/', evaluate_response),
    
    # Person 2 endpoints
    path("start/", start_interview, name="interview_start"),
    path("answer/", submit_answer, name="interview_answer"),
    path("evaluate/", evaluate_answer, name="interview_evaluate"),
    path("report/", interview_report, name="interview_report"),
    path("history/", interview_history, name="interview_history"),
    
    # Specific Checklist Wrappers
    path("generate-hr-question/", generate_hr_question, name="generate_hr_question"),
    path("evaluate-hr-response/", evaluate_hr_response, name="evaluate_hr_response"),
    path("generate-behavioral-question/", generate_behavioral_question, name="generate_behavioral_question"),
    path("evaluate-behavioral-response/", evaluate_behavioral_response, name="evaluate_behavioral_response"),
]