import time

import pytest


@pytest.mark.performance
def test_health_endpoint_latency(api_client):
    started_at = time.perf_counter()
    response = api_client.get("/health/")
    elapsed_ms = (time.perf_counter() - started_at) * 1000

    assert response.status_code == 200
    assert elapsed_ms < 250


@pytest.mark.performance
def test_mongodb_count_latency(mongo_ready):
    from utils.mongo_documents import InterviewSession

    started_at = time.perf_counter()
    InterviewSession.objects.count()
    elapsed_ms = (time.perf_counter() - started_at) * 1000

    assert elapsed_ms < 500


@pytest.mark.performance
def test_evaluation_latency():
    from services.ai.evaluation_engine import EvaluationEngine

    started_at = time.perf_counter()
    EvaluationEngine().evaluate(
        {
            "role": "Java Backend Developer",
            "mode": "technical",
            "question": "Explain service boundaries.",
            "difficulty": "medium",
            "answer_text": "I separate controller, service, and repository responsibilities and test failure cases.",
            "speech_metrics": {"filler_count": 0, "pause_count": 0, "duration_seconds": 12, "words_per_minute": 125},
            "vision_metrics": {"attention": "partial", "eye_contact_score": 65, "emotion_score": 0.6},
            "skills": ["Java", "Spring Boot", "testing"],
        }
    )
    elapsed = time.perf_counter() - started_at

    assert elapsed < 2.0
