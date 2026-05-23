# HireSenseAI Features Log

## 2026-05-22

### Added

- Added hosted frame upload endpoint `POST /api/vision/frame/` with `image_base64` support.
- Added base64 support for `/api/vision/analyze/` to accept JSON payloads.
- Added automated API tests covering frame upload base64 payloads.

### Documentation

- Updated README vision API guidance for base64 and hosted frame uploads.

## 2026-05-21

### Added

- Added xAI Grok provider module plus local Hugging Face provider with timeout-aware fallback chaining.
- Added local HF enable flags and generation controls in `.env.example`.
- Added admin transcript inspection and report summary panels in the Mongo-backed admin views.
- Added MongoDB index enforcement on connection to keep collections consistent across restarts.
- Added `run_realtime_interview` management command for webcam + microphone interview loops.
- Added Celery-ready task queue dispatch and realtime event bus scaffolding.

### Changed

- Switched LLM abstraction to xAI Grok with local Hugging Face fallback.
- Replaced Google SpeechRecognition with an optional HTTP online recognizer.
- Updated MongoDB environment variable names to `MONGO_URI` and `MONGO_DB_NAME`.

### Documentation

- Updated architecture, project context, README, and deployment guidance for Grok, local HF, and MongoDB Compass workflows.

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
- Added LLM abstraction for xAI Grok and local Hugging Face with retry/timeout handling and JSON parsing.
- Added local fallback interviewer so the platform works without paid API keys.
- Added answer evaluation for technical quality, communication, confidence, and hesitation.
- Added adaptive difficulty and contextual follow-up generation.
- Added MongoDB-backed interview memory and final report persistence.
- Added REST APIs for start, answer, evaluate, and report.
- Added uploaded audio transcription support for answer submission.
- Added mandatory pytest QA suite under `backend/tests/`.
- Added hardware-gated webcam and microphone validation tests.
- Added performance checks for endpoint latency, Mongo query speed, and evaluation latency.
- Added dependency checks for TensorFlow, FER, OpenCV, MediaPipe, Vosk, and PyAudio.
- Added offline-first speech package under `backend/services/speech/`.
- Added Vosk dependency and `VOSK_MODEL_PATH` configuration.
- Added optional online speech recognition flag: `ALLOW_ONLINE_SPEECH_RECOGNITION`.
- Added confidence engine under `backend/services/confidence_engine.py`.
- Added `POST /api/speech/transcribe/`.
- Added `POST /api/vision/analyze/`.
- Added backend-only local interview command: `python backend/manage.py run_local_interview`.
- Added WhiteNoise deployment static serving, `render.yaml`, and `Procfile`.
- Changed default xAI Grok model to `grok-2-latest`.

### Bug Fixes

- Replaced incompatible dependency pins from Django 6, NumPy 2.x, and MediaPipe 0.10.33 with the stable project versions.
- Fixed Django settings module naming after scaffolding through a temporary package name.
- Retired the Google SpeechRecognition dependency in favor of offline-first transcription.
- Installed missing `PyAudio==0.2.14` after live microphone validation failed.
- Installed missing `vosk==0.3.45` for offline speech architecture.
- Installed missing `whitenoise==6.11.0` and `gunicorn==23.0.0` after deployment middleware validation exposed missing packages.
- Fixed QA tests to use Django admin session authentication instead of DRF token authentication for admin pages.
- Fixed duplicate email persistence test to assert `NotUniqueError` without reloading an unsaved duplicate document.
- Ran `collectstatic --noinput` to validate WhiteNoise static directory generation.

### Pending

- Browser UI for live interview flow.
- Client-side webcam frame streaming into `vision_metrics`.
- Download and configure a local Vosk model directory for real offline transcription, then set `VOSK_MODEL_PATH`.
