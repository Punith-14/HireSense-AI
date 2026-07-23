# HireSense AI

HireSense AI is an AI-powered adaptive mock interview platform with a React frontend and a Django backend. It runs technical, HR, and behavioral interviews through multiple AI agents, adapts question difficulty to answer quality, challenges the candidate with debate-style follow-ups, analyzes webcam emotion and voice delivery, and visualizes progress across every past interview on a dashboard.

## Project Overview

### Core capabilities

- Multi-agent AI interviewers for `technical`, `hr`, and `behavioral` interviews
- AI answer evaluation with structured feedback and per-skill scores
- Adaptive difficulty driven by score thresholds (good answer → harder, weak → easier)
- Debate-mode follow-ups that pressure-test the candidate's own answer
- Signal-based confidence scoring fused from speech (pace, pauses, filler words) and webcam (eye contact)
- Composure/emotion timeline from webcam analysis
- Token-based authentication; all interview data is scoped per user
- Immersive, full-screen "interview room" with spoken questions (text-to-speech) and warn-once proctoring
- Cross-session progress dashboard: score trend, per-skill trend, best/average, and improvement vs the previous test
- Interview reports and per-user history persisted in MongoDB

### Tech stack

#### Frontend

- React
- Vite
- React Router
- Axios
- Recharts
- Framer Motion
- Lucide React

#### Backend

- Django
- Django REST Framework
- LangChain
- Groq (Llama 3.1 8B Instant for questions + Llama 3.3 70B Versatile for evaluation)
- OpenRouter (DeepSeek R1, used by the behavioral evaluator)
- MongoEngine / MongoDB (interview, report, and user persistence)
- SQLite (Django's built-in tables only)
- Celery + Redis (optional background tasks)
- OpenCV + MediaPipe + FER (webcam emotion & eye-contact analysis)
- Vosk (optional offline speech-to-text for voice answers)

Authentication uses Django's built-in signed tokens (`django.core.signing`) — no extra dependency. Spoken questions in the interview room use the browser's built-in Web Speech API (no backend, no key).

## Repository Structure

```text
HireSense_AI/
|-- backend/              # Django backend
|-- frontend/             # React frontend
|-- venv/                 # Python virtual environment
|-- requirements.txt
`-- README.md
```

### Important backend areas

```text
backend/
|-- backend/              # Django project config
|-- interview/            # Interview APIs and AI routing
|-- speech/               # Speech transcription API
|-- vision/               # Vision / emotion analysis API
|-- users/                # User registration and login APIs
|-- services/             # Shared service-layer logic
|-- reports/              # Reporting-related modules
|-- utils/                # MongoEngine document models and helpers
`-- config/               # MongoDB connection helpers
```

### Important frontend areas

```text
frontend/src/
|-- components/
|-- context/
|-- pages/
|-- routes/
`-- services/
```

## Frontend Pages

The frontend includes:

- Home (public)
- About (public)
- Login / Signup (public)
- Interview Setup (requires login)
- Interview Session — the immersive interview room (requires login)
- Dashboard (requires login)
- History (requires login)

Protected pages are guarded by `ProtectedRoute`; without a token the user is redirected to `/login`. The navbar and footer are hidden while the interview room is active.

## Authentication

- `POST /api/users/register/` and `POST /api/users/login/` return a signed token plus the user object.
- The frontend stores the token in `localStorage` and an Axios interceptor attaches it as `Authorization: Bearer <token>` on every request. A 401 auto-logs-out and redirects to login.
- Every API endpoint except register/login requires a valid token (DRF `DEFAULT_PERMISSION_CLASSES = IsAuthenticated`). Interview sessions and history are scoped to the authenticated user.
- Tokens expire after 7 days. Passwords are hashed with Django's password hashers.

## Interview Experience (Interview Room)

The session page is a full-screen interview room rather than a chat window:

- The AI interviewer reads each question aloud (browser text-to-speech, with mute/replay).
- One question is shown at a time with a speaking avatar and turn cues (asking / your turn / recording / evaluating).
- Voice-first answering (record button) with typing as a fallback.
- Warn-once proctoring: leaving the window (tab switch or exiting full-screen) warns once, then closes the interview and returns to the dashboard with an explanation.

## Backend API Summary

Base backend URL:

```text
http://127.0.0.1:8000/
```

### Interview APIs

Prefix:

```text
/api/interview/
```

#### Person 1 core endpoints

- `POST /api/interview/generate-question/`
- `POST /api/interview/evaluate-response/`

These endpoints use `interview_type` and support:

- `technical`
- `hr`
- `behavioral`

Example request:

```json
{
  "interview_type": "technical",
  "role": "Java Developer",
  "difficulty": "medium"
}
```

Example evaluation request:

```json
{
  "interview_type": "technical",
  "question": "Explain polymorphism in Java.",
  "answer": "Polymorphism allows objects to take many forms."
}
```

Technical evaluations also return `next_difficulty`.

#### Extended interview/session endpoints

- `POST /api/interview/start/`
- `POST /api/interview/answer/`
- `POST /api/interview/evaluate/`
- `GET /api/interview/report/?session_id=...`
- `GET /api/interview/history/`

#### Checklist wrapper endpoints

- `POST /api/interview/generate-hr-question/`
- `POST /api/interview/evaluate-hr-response/`
- `POST /api/interview/generate-behavioral-question/`
- `POST /api/interview/evaluate-behavioral-response/`

### Other API groups

- `POST /api/speech/transcribe/`
- `POST /api/vision/analyze/`
- `POST /api/users/register/`
- `POST /api/users/login/`

> All endpoints except `register/` and `login/` require an `Authorization: Bearer <token>` header. `GET /api/interview/history/` returns per-session scores (overall + technical/communication/confidence + mode) for the logged-in user, which the dashboard uses to build the progress trend.

## Local Setup

### 1. Clone or open the project

Work from:

```text
HireSense_AI/
```

### 2. Python backend setup

If the virtual environment already exists:

```powershell
cd backend
..\venv\Scripts\activate
```

If you need to install dependencies:

```powershell
pip install -r ..\requirements.txt
```

### 3. Backend environment variables

Create:

```text
backend/.env
```

Recommended variables:

```env
# AI providers
GROQ_API_KEY=your_groq_api_key
OPENROUTER_API_KEY=your_openrouter_api_key   # optional; used by the behavioral evaluator

# Database
MONGO_URI=mongodb://localhost:27017/hiresense_ai
MONGO_DB_NAME=hiresense_ai

# Django / security (defaults keep local dev working)
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=change-this-for-production
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=                          # required only when DJANGO_DEBUG=False

# Optional voice answers
VOSK_MODEL_PATH=                               # path to a downloaded Vosk model

# Optional background tasks
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_ALWAYS_EAGER=True
```

A complete, annotated template is available at `backend/.env.example` — copy it to `backend/.env` and fill in your keys.

Notes:

- `GROQ_API_KEY` is required for question generation and evaluation. Get one at https://console.groq.com.
- MongoDB is used for all interview, report, and user persistence.
- Redis/Celery is optional unless you are using background task execution.
- `VOSK_MODEL_PATH` is optional — set it (download a model from https://alphacephei.com/vosk/models) to enable offline transcription so the confidence score picks up voice signals. Without it, spoken answers fall back to typing and confidence uses webcam signals only.
- In local debug mode, Mongo connection failures are deferred instead of crashing startup.

### Production security

Security settings are environment-driven and default to safe local development. For production, set `DJANGO_DEBUG=False` and provide a real `DJANGO_SECRET_KEY`, your domain in `DJANGO_ALLOWED_HOSTS`, and your frontend URL in `CORS_ALLOWED_ORIGINS`. With `DEBUG=False` the app enforces the secret key, restricts CORS to the allowlist, and enables HTTPS/HSTS/secure-cookie hardening. With `DEBUG=True` all of that is a no-op and CORS stays open.

### 4. Run the backend

From `HireSense_AI/backend`:

```powershell
..\venv\Scripts\python.exe manage.py runserver
```

Backend will run at:

```text
http://127.0.0.1:8000/
```

### 5. Frontend setup

From `HireSense_AI/frontend`:

```powershell
C:\Program Files\nodejs\npm.cmd install
```

### 6. Run the frontend

From `HireSense_AI/frontend`:

```powershell
C:\Program Files\nodejs\npm.cmd run dev
```

Frontend will run at:

```text
http://127.0.0.1:5173/
```

### 7. Build the frontend

```powershell
C:\Program Files\nodejs\npm.cmd run build
```

## Testing

### Backend interview tests

Run the quota-safe mocked interview API tests:

```powershell
cd backend
..\venv\Scripts\python.exe manage.py test interview
```

These tests verify:

- interview type routing
- technical/HR/behavioral evaluation flow
- adaptive difficulty response
- request validation

### Notes about model quota

If the Groq/OpenRouter quota is exhausted, evaluators fall back to safe default responses and the mocked Django tests can still validate the backend logic without making live model calls.

## Data Model & Maintenance

Interview data lives in MongoDB via MongoEngine documents in `backend/utils/mongo_documents.py`:

- `UserProfile` — one per user (unique email).
- `InterviewSession` — one per interview attempt.
- `Interview` — questions, transcript, and scores for a session (unique per session).
- `Report` — the final scorecard for an interview (unique per interview), tied to the user with a timestamp, per-skill scores, and `mode`. This is the record the per-user progress dashboard reads.

The one-to-one relationships are enforced with unique indexes, and `Report` has a compound `(user, created_at)` index for the "this user's tests, newest first" query.

If an older dev database already contains duplicate rows, the unique indexes will refuse to build. Use the maintenance script to inspect or clean it:

```powershell
cd backend
..\venv\Scripts\python.exe scripts\check_duplicates.py            # report only (safe)
..\venv\Scripts\python.exe scripts\check_duplicates.py --fix      # remove older duplicates, keep newest
..\venv\Scripts\python.exe scripts\check_duplicates.py --drop     # drop interview collections for a clean rebuild
```

## Current Frontend Flow

The frontend currently follows this shape:

```text
Home
-> Interview Setup
-> Interview Session
-> Dashboard
-> History
-> About
```

Interview flow:

```text
Log in
-> Select role & agent & preferences
-> Enter interview room (full-screen, question spoken aloud)
-> Answer (voice or typing)
-> AI evaluation + confidence/composure from webcam & voice
-> Adaptive next question or debate-style challenge
-> Repeat (5 questions) -> Dashboard & progress trend
```

## Current Backend Flow

The interview room drives the stateful engine in `backend/services/ai/interview_engine.py`, which uses the routing/agents in `backend/interview/`:

1. `start/` creates a session and asks the first question (multi-agent by mode).
2. `answer/` evaluates the response, fuses a confidence score from speech + webcam signals, stores it, computes the adaptive `next_difficulty`, and returns either a debate-style challenge or the next question.
3. Scores are aggregated across answers (averaged, no fabricated defaults) and written to a `Report`.
4. `report/` and `history/` feed the dashboard and the per-user progress trend.

Stateless "Person 1" endpoints (`generate-question/`, `evaluate-response/`) remain available for direct/testing use via `interview_router.py`.

## Important Notes

- Security settings are environment-driven; CORS is open only in local `DEBUG` mode (see Production security above).
- Static files are configured with WhiteNoise.
- SQLite holds only Django's built-in tables; all app data is in MongoDB.
- All API endpoints except register/login require a bearer token.
- Some duplicate or legacy modules exist in the repo due to ongoing project growth; use the URLs and entry points documented here as the primary starting path.

## Recommended Start Points

If you are working on the project now, these are the most useful entry points:

- Backend app config: [settings.py](C:\Users\punit\OneDrive\Desktop\project\HireSense_AI\backend\backend\settings.py)
- Backend URLs: [urls.py](C:\Users\punit\OneDrive\Desktop\project\HireSense_AI\backend\backend\urls.py)
- Interview APIs: [views.py](C:\Users\punit\OneDrive\Desktop\project\HireSense_AI\backend\interview\views.py)
- Interview routing service: [interview_router.py](C:\Users\punit\OneDrive\Desktop\project\HireSense_AI\backend\interview\services\interview_router.py)
- Frontend routes: [AppRoutes.jsx](C:\Users\punit\OneDrive\Desktop\project\HireSense_AI\frontend\src\routes\AppRoutes.jsx)
- Frontend app shell: [App.jsx](C:\Users\punit\OneDrive\Desktop\project\HireSense_AI\frontend\src\App.jsx)

## Status

Current state of the repo:

- Multi-agent adaptive interview backend implemented (technical / HR / behavioral)
- Debate-mode follow-ups and signal-based confidence scoring implemented
- Token authentication with per-user data scoping implemented
- Immersive interview room with spoken questions and warn-once proctoring implemented
- Dashboard with single-test results, composure timeline, and cross-session progress trend implemented
- MongoDB schema with unique indexes and a duplicate-cleanup maintenance script
- Mocked backend tests available

Known follow-ups:

- Voice-answer confidence requires a configured Vosk model (`VOSK_MODEL_PATH`).
- The About page still lacks the architecture/tech/team sections.
- Browser text-to-speech voice quality varies by OS/browser.
