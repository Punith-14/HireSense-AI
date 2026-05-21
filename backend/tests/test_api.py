def test_health_endpoint(api_client):
    response = api_client.get("/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_start_interview_requires_role(api_client):
    response = api_client.post("/api/interview/start/", {"mode": "technical"}, format="json")

    assert response.status_code == 400
    assert response.json()["error"] == "role is required"


def test_start_answer_report_flow(api_client, qa_email, mongo_ready):
    start = api_client.post(
        "/api/interview/start/",
        {"role": "Python Developer", "mode": "technical", "user_email": qa_email},
        format="json",
    )
    assert start.status_code == 200
    start_payload = start.json()
    assert start_payload["question"]["question"]
    assert start_payload["question"]["difficulty"] in {"easy", "medium", "hard"}

    answer = api_client.post(
        "/api/interview/answer/",
        {
            "session_id": start_payload["session_id"],
            "answer_text": (
                "I would design the API with service boundaries, validation, idempotent writes, "
                "MongoDB indexes, and failure-mode tests because production reports must not duplicate."
            ),
            "speech_metrics": {
                "filler_count": 1,
                "pause_count": 1,
                "duration_seconds": 34,
                "words_per_minute": 130,
            },
            "vision_metrics": {"attention": "direct", "eye_contact_score": 84, "emotion_score": 0.7},
        },
        format="json",
    )
    assert answer.status_code == 200
    answer_payload = answer.json()
    assert 0 <= answer_payload["evaluation"]["technical_score"] <= 100
    assert answer_payload["next_question"]["question"]
    assert answer_payload["next_question"]["question"] != start_payload["question"]["question"]

    report = api_client.get("/api/interview/report/", {"session_id": start_payload["session_id"]})
    assert report.status_code == 200
    report_payload = report.json()["report"]
    assert report_payload["final_score"] >= 0
    assert report_payload["hiring_recommendation"] in {"proceed", "borderline", "do_not_proceed"}


def test_evaluate_unknown_session_returns_404(api_client):
    response = api_client.post(
        "/api/interview/evaluate/",
        {"session_id": "000000000000000000000000", "answer_text": "test"},
        format="json",
    )

    assert response.status_code == 404


def test_speech_transcribe_text_metrics_api(api_client):
    response = api_client.post(
        "/api/speech/transcribe/",
        {"text": "Um I would use indexes and tests because reliability matters.", "duration_seconds": 8},
        format="json",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "text_metrics_only"
    assert payload["metrics"]["filler_count"] == 1


def test_vision_analyze_requires_image(api_client):
    response = api_client.post("/api/vision/analyze/", {}, format="multipart")

    assert response.status_code == 400


def test_vision_analyze_blank_image_api(api_client):
    import cv2
    import numpy as np
    from django.core.files.uploadedfile import SimpleUploadedFile

    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    ok, encoded = cv2.imencode(".jpg", frame)
    assert ok
    upload = SimpleUploadedFile("frame.jpg", encoded.tobytes(), content_type="image/jpeg")

    response = api_client.post("/api/vision/analyze/", {"image_file": upload}, format="multipart")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "vision" in payload
    assert "confidence" in payload
