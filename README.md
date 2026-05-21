# HireSenseAI

Production-grade AI-powered adaptive mock interview intelligence platform.

## Current Backend

The backend lives in `backend/` and uses Django 5, Django REST Framework, MongoDB, MongoEngine, OpenCV, MediaPipe, FER, TensorFlow, SpeechRecognition, and PyAudio.

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
