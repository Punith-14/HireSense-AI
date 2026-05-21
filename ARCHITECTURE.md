# HireSenseAI Architecture

Last updated: 2026-05-20

## Backend Architecture

The backend is Django 5 plus Django REST Framework. Django owns routing, API/auth/admin infrastructure, and operational views. Domain persistence uses MongoDB through MongoEngine, centralized through `backend/config/db.py`.

SQLite is retained only for Django's built-in admin authentication tables unless a later phase replaces admin auth with a Mongo-aware auth backend. Interview domain data is not stored in SQLite.

## Database Design

MongoDB collections:

- `users`: user profile, auth provider, interview history, indexed by unique email.
- `sessions`: runtime metadata for active/completed interview sessions, indexed by role/status/session key.
- `interviews`: transcript, questions, scores, and AI feedback, indexed by role/mode/session/user.
- `reports`: final analysis, recommendations, score fields, dominant emotion, indexed for admin filtering.

Documents use `created_at` and `updated_at`. Collections are not recreated on restart; MongoEngine only defines indexes and persists data normally.

## API Structure

Initial app boundaries are in place:

- `interview`: interview lifecycle and adaptive question APIs.
- `vision`: frame processing APIs and local live CV tooling.
- `speech`: audio ingestion and speech analytics APIs.
- `scoring`: score aggregation APIs.
- `reports`: report generation and retrieval APIs.
- `users`: profile APIs.

Implemented interview endpoints:

- `POST /api/interview/start/`: creates MongoDB session/interview and returns the first adaptive question.
- `POST /api/interview/answer/`: accepts `answer_text` or `audio_file`, evaluates the answer, updates memory, and returns the next contextual question.
- `POST /api/interview/evaluate/`: evaluates an answer without advancing the interview.
- `GET /api/interview/report/?session_id=...`: generates and persists the final report.
- `POST /api/speech/transcribe/`: accepts `text` for metrics-only analysis or `audio_file` for offline-first transcription.
- `POST /api/vision/analyze/`: accepts an uploaded image frame and returns emotion, attention, and confidence signals.

## AI Service Architecture

`backend/services/ai/` contains the core intelligence engine:

- `llm_service.py`: cached HTTP session, xAI Grok + local Hugging Face provider abstraction, retries, timeouts, structured JSON parsing, local fallback.
- `grok_provider.py`: xAI Grok chat completion provider with retry/timeout handling.
- `hf_provider.py`: local Hugging Face model loader and generation helper.
- `prompt_engine.py`: centralized prompt templates and role skill inference.
- `evaluation_engine.py`: technical, communication, confidence, and hesitation scoring from answer text, speech metrics, and vision metrics.
- `adaptive_engine.py`: difficulty and pressure-level decisions.
- `memory_engine.py`: MongoDB-backed interview state, transcript, question history, and report persistence.
- `interview_engine.py`: orchestration layer used by APIs.

Questions are dynamically generated from role, difficulty, skill coverage, previous questions, and previous answer context. The fallback path uses a role skill taxonomy and contextual templates, not fixed question lists.

## ML Pipeline

Vision processing loads FER and MediaPipe through cached accessors so TensorFlow-backed models are not repeatedly initialized per frame. Local webcam processing is supported by `vision.management.commands.run_live_cv`.

Hosted deployment cannot access a user's webcam directly. Production architecture should receive browser-captured frames through upload endpoints first, then WebSocket streaming when needed.

LLM calls use a primary xAI Grok provider with a local Hugging Face fallback:

- `XAI_API_KEY` with `XAI_MODEL=grok-2-latest`
- `HF_LOCAL_ENABLED=True` with `HF_MODEL=microsoft/Phi-3-mini-4k-instruct` (or another local model)

If the provider is unavailable or disabled, the backend uses deterministic local fallback generation and scoring so live development remains functional.

## Speech Architecture

`backend/services/speech/` is offline-first:

- `speech_service.py`: orchestrates recognizer selection and never hard-fails because the internet is unavailable.
- `offline_recognizer.py`: Vosk integration using `VOSK_MODEL_PATH` for local models.
- `online_recognizer.py`: optional HTTP fallback only when `ALLOW_ONLINE_SPEECH_RECOGNITION=True` and `ONLINE_SPEECH_ENDPOINT` is set.
- `filler_detector.py`: filler word detection.
- `pause_detector.py`: WAV pause detection using local audio analysis.
- `speech_metrics.py`: word count, WPM, hesitation, filler, pause, and communication metrics.

Provider priority is offline Vosk, then optional online recognition, then graceful `transcription_unavailable` with metrics where possible.

## Runtime Architecture

`backend/services/runtime/task_executor.py` provides a cached `ThreadPoolExecutor` for inference isolation. `task_queue.py` adds a Celery-ready dispatch layer, and `realtime_bus.py` defines event payloads for future WebSocket streaming. The current APIs remain synchronous for simplicity, but ML/model clients are cached and the runtime boundary is ready for queue or streaming upgrades.

## CV Processing Pipeline

1. Capture frame locally or receive frame from client.
2. Convert BGR to RGB for MediaPipe.
3. Run cached FER emotion detection.
4. Run cached MediaPipe face mesh.
5. Estimate attention from eye/nose landmarks.
6. Persist aggregate metrics to sessions/interviews/reports only at controlled intervals.

## Deployment Flow

Render runs Django with environment variables. MongoDB Atlas free tier supplies `MONGO_URI`. Static files are collected with `collectstatic`. Domain documents remain in MongoDB.

## QA Architecture

Automated tests live under `backend/tests/`:

- `test_api.py`: health route, validation failures, start/answer/report API flow.
- `test_db.py`: MongoDB health, unique email enforcement, persistence after reconnect, index presence.
- `test_ai.py`: adaptive decisions, answer scoring, fallback interview latency.
- `test_cv.py`: OpenCV/MediaPipe/TensorFlow/FER imports, cached model clients, blank-frame processing, hardware webcam probe.
- `test_speech.py`: text speech metrics, sounddevice dependency, Vosk dependency, offline-unavailable fallback behavior, microphone probe.
- `test_integration.py`: AI + speech metrics + vision metrics + report persistence, admin page stability.
- `test_performance.py`: health endpoint latency, MongoDB query latency, evaluation latency.

Hardware tests are guarded by `RUN_LIVE_HARDWARE_TESTS=1` so CI-safe runs do not fail on machines without cameras or microphones.
