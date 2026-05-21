# HireSenseAI Project Context

Last updated: 2026-05-20

## Current State

HireSenseAI now has a Django 5 backend scaffold under `backend/`, MongoEngine document models for persistent MongoDB collections, a Django admin operations console, and a local live webcam CV command.

## Folder Structure

- `backend/backend/`: Django settings, URLs, ASGI/WSGI, admin views.
- `backend/config/`: environment-driven infrastructure configuration. `db.py` owns MongoDB connection initialization.
- `backend/utils/`: shared domain documents and utility code.
- `backend/interview/`: interview engine app boundary.
- `backend/vision/`: CV processing app boundary and local webcam command.
- `backend/speech/`: speech analysis app boundary.
- `backend/scoring/`: scoring engine app boundary.
- `backend/reports/`: AI report app boundary.
- `backend/users/`: Django auth admin customization plus MongoDB user profile boundary.
- `datasets/`: dataset download/preprocessing workspace.

## Current Progress

- Django project scaffolded.
- Environment variables wired through `.env`.
- MongoDB connection centralized in `backend/config/db.py`.
- MongoEngine collections defined: `users`, `sessions`, `interviews`, `reports`.
- Django admin available at `/admin`.
- HireSenseAI Mongo admin pages available under `/admin/hiresense/...`.
- Local live webcam command added: `python backend/manage.py run_live_cv`.
- Adaptive AI interview service layer added under `backend/services/ai/`.
- Interview APIs added:
  - `POST /api/interview/start/`
  - `POST /api/interview/answer/`
  - `POST /api/interview/evaluate/`
  - `GET /api/interview/report/?session_id=...`
- Answer submission supports `answer_text` or uploaded `audio_file`.
- Automated QA suite added under `backend/tests/` with API, DB, AI, CV, speech, integration, and performance coverage.
- Live hardware validation passed with webcam and microphone probes using `RUN_LIVE_HARDWARE_TESTS=1`.
- Offline-first speech service added under `backend/services/speech/` with Vosk support, optional online fallback, filler detection, pause detection, and speech metrics.
- Standalone backend APIs added:
  - `POST /api/speech/transcribe/`
  - `POST /api/vision/analyze/`
- Groq `llama3-8b-8192` is now the default primary adaptive interview model through the centralized LLM abstraction layer, with Hugging Face fallback support.
- Deployment readiness files added: `render.yaml`, `Procfile`, WhiteNoise static serving, and `collectstatic` validation.

## Module Overview

- Interview Engine: starts sessions, generates dynamic questions, evaluates answers, creates next questions, and generates reports.
- Vision Engine: currently supports live frame processing with OpenCV, MediaPipe, and FER.
- Speech Engine: offline-first Vosk architecture, optional online fallback, uploaded audio metrics, filler detection, pause detection, speaking speed.
- Scoring Engine: confidence, hesitation, communication, technical, and final scoring are computed in the evaluation pipeline.
- Report Engine: creates final structured analysis and recommendation.
- QA Harness: pytest validates dependency imports, MongoDB persistence, adaptive interview APIs, cached CV services, speech analysis, admin pages, and performance budgets.
- Backend-only local operation: `python backend/manage.py run_local_interview` drives an adaptive terminal interview without frontend dependencies.
