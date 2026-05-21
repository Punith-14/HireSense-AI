# HireSenseAI Features Log

## 2026-05-20

### Added

- Created Django backend scaffold under `backend/`.
- Added modular apps: `interview`, `vision`, `speech`, `scoring`, `reports`, `users`.
- Added centralized MongoDB connection layer at `backend/config/db.py`.
- Added MongoEngine document models for `users`, `sessions`, `interviews`, and `reports`.
- Added professional Django admin branding and custom auth user admin.
- Added MongoDB-backed admin views:
  - `/admin/hiresense/users/`
  - `/admin/hiresense/sessions/`
  - `/admin/hiresense/interviews/`
  - `/admin/hiresense/reports/`
- Added local live webcam CV command: `python backend/manage.py run_live_cv`.
- Added `.env.example`.
- Corrected dependency pins to stable Python 3.11-compatible ML versions.
- Added adaptive AI interview engine under `backend/services/ai/`.
- Added LLM abstraction for Groq and Hugging Face with retry/timeout handling and JSON parsing.
- Added local fallback interviewer so the platform works without paid API keys.
- Added answer evaluation for technical quality, communication, confidence, and hesitation.
- Added adaptive difficulty and contextual follow-up generation.
- Added MongoDB-backed interview memory and final report persistence.
- Added REST APIs for start, answer, evaluate, and report.
- Added uploaded audio transcription support for answer submission.
- Added mandatory pytest QA suite under `backend/tests/`.
- Added hardware-gated webcam and microphone validation tests.
- Added performance checks for endpoint latency, Mongo query speed, and evaluation latency.
- Added dependency checks for TensorFlow, FER, OpenCV, MediaPipe, SpeechRecognition, and PyAudio.
- Added offline-first speech package under `backend/services/speech/`.
- Added Vosk dependency and `VOSK_MODEL_PATH` configuration.
- Added optional online speech recognition flag: `ALLOW_ONLINE_SPEECH_RECOGNITION`.
- Added confidence engine under `backend/services/confidence_engine.py`.
- Added `POST /api/speech/transcribe/`.
- Added `POST /api/vision/analyze/`.
- Added backend-only local interview command: `python backend/manage.py run_local_interview`.
- Added WhiteNoise deployment static serving, `render.yaml`, and `Procfile`.
- Changed default Groq model to `llama3-8b-8192`.

### Bug Fixes

- Replaced incompatible dependency pins from Django 6, NumPy 2.x, and MediaPipe 0.10.33 with the stable project versions.
- Fixed Django settings module naming after scaffolding through a temporary package name.
- Installed missing `SpeechRecognition==3.16.1` into the active venv after API import validation exposed the missing module.
- Installed missing `PyAudio==0.2.14` after live microphone validation failed.
- Installed missing `vosk==0.3.45` for offline speech architecture.
- Installed missing `whitenoise==6.11.0` and `gunicorn==23.0.0` after deployment middleware validation exposed missing packages.
- Fixed QA tests to use Django admin session authentication instead of DRF token authentication for admin pages.
- Fixed duplicate email persistence test to assert `NotUniqueError` without reloading an unsaved duplicate document.
- Ran `collectstatic --noinput` to validate WhiteNoise static directory generation.

### Pending

- Browser UI for live interview flow.
- Client-side webcam frame streaming into `vision_metrics`.
- Frame upload endpoint for hosted deployments.
- Automated frame-upload API tests after that endpoint is built.
- Download and configure a local Vosk model directory for real offline transcription, then set `VOSK_MODEL_PATH`.
