import time


def test_adaptive_engine_increases_for_strong_answer():
    from services.ai.adaptive_engine import AdaptiveEngine

    decision = AdaptiveEngine().decide(
        {
            "technical_score": 90,
            "communication_score": 82,
            "confidence_score": 85,
            "hesitation_score": 20,
        },
        "medium",
    )

    assert decision["next_difficulty"] == "hard"
    assert decision["follow_up_recommended"] is True


def test_adaptive_engine_reduces_for_weak_hesitant_answer():
    from services.ai.adaptive_engine import AdaptiveEngine

    decision = AdaptiveEngine().decide(
        {
            "technical_score": 35,
            "communication_score": 42,
            "confidence_score": 30,
            "hesitation_score": 85,
        },
        "medium",
    )

    assert decision["next_difficulty"] == "easy"
    assert decision["pressure_level"] == "supportive"


def test_evaluation_engine_scores_answer_with_metrics():
    from services.ai.evaluation_engine import EvaluationEngine

    evaluation = EvaluationEngine().evaluate(
        {
            "role": "Python Developer",
            "mode": "technical",
            "question": "How would you design a scoring API?",
            "difficulty": "medium",
            "answer_text": "I would use validation, idempotent writes, indexes, tests, and failure handling.",
            "speech_metrics": {"filler_count": 0, "pause_count": 1, "duration_seconds": 20, "words_per_minute": 120},
            "vision_metrics": {"attention": "direct", "eye_contact_score": 80, "emotion_score": 0.7},
            "skills": ["Python", "REST APIs", "databases", "testing"],
        }
    )

    assert 0 <= evaluation["technical_score"] <= 100
    assert 0 <= evaluation["confidence_score"] <= 100
    assert evaluation["next_difficulty"] in {"easy", "medium", "hard"}


def test_interview_engine_fallback_latency(mongo_ready, qa_email):
    from services.ai.interview_engine import InterviewEngine

    started_at = time.perf_counter()
    result = InterviewEngine().start("MERN Stack Developer", user_email=qa_email)
    elapsed = time.perf_counter() - started_at

    assert result["question"]["question"]
    assert elapsed < 3.0


def test_llm_service_defaults_to_requested_groq_model(monkeypatch):
    from services.ai.llm_service import LLMService

    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    service = LLMService()
    status = service.provider_status()

    assert status["provider"] == "groq"
    assert status["groq_model"] == "llama3-8b-8192"
    assert status["fallback_enabled"] is True
