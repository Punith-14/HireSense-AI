def test_ai_speech_vision_report_integration(api_client, qa_email, mongo_ready):
    start = api_client.post(
        "/api/interview/start/",
        {"role": "Data Scientist", "mode": "technical", "user_email": qa_email},
        format="json",
    )
    assert start.status_code == 200
    session_id = start.json()["session_id"]

    answer = api_client.post(
        "/api/interview/answer/",
        {
            "session_id": session_id,
            "answer_text": (
                "I would define the target variable, check leakage, build a baseline, "
                "use cross validation, and compare precision recall tradeoffs."
            ),
            "speech_metrics": {"filler_count": 0, "pause_count": 1, "duration_seconds": 28, "words_per_minute": 135},
            "vision_metrics": {"attention": "direct", "eye_contact_score": 86, "emotion_score": 0.75},
        },
        format="json",
    )
    assert answer.status_code == 200
    assert answer.json()["evaluation"]["confidence_score"] >= 50

    report = api_client.get("/api/interview/report/", {"session_id": session_id})
    assert report.status_code == 200
    assert report.json()["report"]["technical_score"] >= 0


def test_admin_hiresense_pages_do_not_500(api_client, django_user_model, mongo_ready):
    user = django_user_model.objects.create_superuser(
        username="qa-admin",
        email="qa-admin@hiresense.test",
        password="qa-admin-password",
    )
    api_client.force_login(user)

    for path in (
        "/admin/hiresense/users/",
        "/admin/hiresense/sessions/",
        "/admin/hiresense/interviews/",
        "/admin/hiresense/reports/",
    ):
        response = api_client.get(path)
        assert response.status_code == 200


def test_answer_endpoint_returns_422_when_audio_has_no_offline_model(api_client, qa_email, tmp_path, monkeypatch, mongo_ready):
    import wave

    monkeypatch.delenv("VOSK_MODEL_PATH", raising=False)
    monkeypatch.setenv("ALLOW_ONLINE_SPEECH_RECOGNITION", "False")
    start = api_client.post(
        "/api/interview/start/",
        {"role": "Python Developer", "mode": "technical", "user_email": qa_email},
        format="json",
    )
    session_id = start.json()["session_id"]
    wav_path = tmp_path / "answer.wav"
    with wave.open(str(wav_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"\x00\x00" * 16000)

    with open(wav_path, "rb") as audio:
        response = api_client.post(
            "/api/interview/answer/",
            {"session_id": session_id, "audio_file": audio},
            format="multipart",
        )

    assert response.status_code == 422
    assert response.json()["status"] == "transcription_unavailable"


def test_local_interview_management_command_is_registered():
    from django.core.management import get_commands

    assert "run_local_interview" in get_commands()
