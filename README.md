# HireSenseAI

Production-grade AI-powered adaptive mock interview intelligence platform.

## Current Backend

The backend lives in `backend/` and uses Django 5, Django REST Framework, MongoDB, MongoEngine, OpenCV, MediaPipe, FER, TensorFlow, xAI Grok API, local Hugging Face (transformers/torch), Vosk, PyAudio, and sounddevice.

## Local Commands

```powershell
cd C:\Users\patel\HireSenseAI
.\venv\Scripts\python.exe backend\manage.py migrate
.\venv\Scripts\python.exe backend\manage.py createsuperuser
.\venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

Admin route:

```text
http://127.0.0.1:8000/admin/
```

Live webcam CV demo:

```powershell
.\venv\Scripts\python.exe backend\manage.py run_live_cv
```

## Frontend Integration Guide

Base URL (local): `http://127.0.0.1:8000`

Core flow:
1. **Start interview** → render first question.
2. **Capture answer** (text or audio) → post to `/api/interview/answer/` with optional speech/vision metrics.
3. **Render next question** until done.
4. **Generate report** with `/api/interview/report/`.

Endpoints (JSON unless noted):

- **POST** `/api/interview/start/`
  - Body: `{ "role": "Python Developer", "mode": "technical", "user_email": "demo@local.test", "full_name": "Demo User" }`
  - Response: `{ "session_id", "interview_id", "role", "mode", "question": { "question", "difficulty", "category", "expected_skills" } }`

- **POST** `/api/interview/answer/`
  - JSON body: `{ "session_id", "answer_text", "speech_metrics": { "filler_count", "pause_count", "duration_seconds", "words_per_minute" }, "vision_metrics": { "attention", "eye_contact_score", "emotion_score" } }`
  - Multipart alternative: `audio_file` plus `session_id`; returns `422` with `transcription_unavailable` if offline model isn’t configured.
  - Response: `{ "session_id", "evaluation": { "technical_score", "communication_score", "confidence_score", "hesitation_score", "next_difficulty" }, "next_question": { ... } }`

- **POST** `/api/interview/evaluate/` (no interview progression)
  - Body: `{ "session_id", "answer_text", "speech_metrics": {...}, "vision_metrics": {...} }`

- **GET** `/api/interview/report/?session_id=...`
  - Response: `{ "report": { "final_analysis", "recommendations", "confidence_score", "behavior_score", "communication_score", "technical_score", "final_score", "hiring_recommendation" } }`

- **POST** `/api/speech/transcribe/`
  - JSON body with `text` + `duration_seconds`, or multipart with `audio_file`.
  - Response includes `status`, `provider`, `transcript`, and `metrics`.

- **POST** `/api/vision/analyze/` (multipart)
  - Form field: `image_file` (JPEG/PNG).
  - Response includes `{ "status": "ok", "vision": { "dominant_emotion", "emotion_score", "attention" }, "confidence": { ... } }`.

Frontend guidance:
- Prefer **text answers** while offline speech models are not installed; switch to audio once `VOSK_MODEL_PATH` is set.
- Send **vision metrics** from client camera if you capture frames client-side; otherwise call `/api/vision/analyze/` periodically and attach results to `/answer/`.
- Handle `422` from `/answer/` by falling back to typed answers.

## Feature Map (How it Works)

| Feature | How it works |
| --- | --- |
| Adaptive questions | LLM generates role-aware questions using difficulty + prior Q/A; deterministic fallback if no provider. |
| Answer evaluation | Heuristics + speech/vision metrics produce technical, communication, confidence, and hesitation scores. |
| Confidence scoring | Combines eye contact, emotion, filler/pauses, and speech speed into confidence/nervousness. |
| Offline speech | Vosk local model transcribes WAV; optional HTTP endpoint fallback if enabled. |
| CV analysis | OpenCV + MediaPipe + FER detect emotion and attention from frames. |
| Reports | LLM summarizes transcript + scores into a final report stored in MongoDB. |
| Admin ops | Django admin for auth + custom Mongo-backed pages for users/sessions/interviews/reports. |
| Persistence | MongoDB collections with enforced indexes to prevent duplicates and ensure restart safety. |
| Realtime loop | `run_realtime_interview` captures webcam + microphone locally without frontend. |

## Adaptive Interview API

Start an interview:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/interview/start/ -ContentType "application/json" -Body '{"role":"Python Developer","mode":"technical","user_email":"demo@local.test"}'
```

Submit an answer:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/interview/answer/ -ContentType "application/json" -Body '{"session_id":"<SESSION_ID>","answer_text":"I would design this with clear service boundaries, indexes, idempotent writes, and tests around failure cases.","speech_metrics":{"filler_count":1,"pause_count":1,"duration_seconds":35,"words_per_minute":128},"vision_metrics":{"attention":"direct","eye_contact_score":82,"emotion_score":0.72}}'
```

Generate report:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/interview/report/?session_id=<SESSION_ID>"
```

Speech metrics/transcription API:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/speech/transcribe/ -ContentType "application/json" -Body '{"text":"Um I would use indexes and tests because reliability matters.","duration_seconds":8}'
```

Vision frame analysis API accepts multipart `image_file`:

```text
POST http://127.0.0.1:8000/api/vision/analyze/
```

Backend-only local interview loop:

```powershell
.\venv\Scripts\python.exe backend\manage.py run_local_interview --role "Python Developer" --turns 3
```

Realtime interview loop (webcam + microphone, offline-first):

```powershell
.\venv\Scripts\python.exe backend\manage.py run_realtime_interview --role "Python Developer" --turns 3
```

## QA Test Suite

Run normal automated tests:

```powershell
.\venv\Scripts\python.exe -m pytest
```

Run full local hardware validation:

```powershell
$env:RUN_LIVE_HARDWARE_TESTS='1'
.\venv\Scripts\python.exe -m pytest
```

Hardware tests validate webcam frame access and microphone device discovery. Keep MongoDB running before executing the suite:

```powershell
Get-Service MongoDB
```
