# HireSenseAI Deployment

Last updated: 2026-05-20

## Local Setup

From `C:\Users\patel\HireSenseAI`:

```powershell
.\venv\Scripts\python.exe --version
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Expected Python version: `3.11.9`.

## Local MongoDB

Use MongoDB Compass or local MongoDB service with:

```text
mongodb://localhost:27017/hiresenseai
```

`.env` values:

```text
MONGODB_URI=mongodb://localhost:27017/hiresenseai
MONGODB_DB_NAME=hiresenseai
```

The connection layer is `backend/config/db.py`. It supports local MongoDB now and MongoDB Atlas later by changing `MONGODB_URI`.

## Django Admin

Create Django admin tables:

```powershell
.\venv\Scripts\python.exe backend\manage.py migrate
```

Create a superuser:

```powershell
.\venv\Scripts\python.exe backend\manage.py createsuperuser
```

Run the server:

```powershell
.\venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8000/admin/
```

Mongo-backed admin pages:

```text
http://127.0.0.1:8000/admin/hiresense/users/
http://127.0.0.1:8000/admin/hiresense/sessions/
http://127.0.0.1:8000/admin/hiresense/interviews/
http://127.0.0.1:8000/admin/hiresense/reports/
```

## Live CV Demo

Run from project root:

```powershell
.\venv\Scripts\python.exe backend\manage.py run_live_cv
```

Use `q` in the OpenCV preview window to stop.

## Render Free Tier

Set environment variables:

```text
DJANGO_SECRET_KEY=<strong-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<render-hostname>.onrender.com
MONGODB_URI=<mongodb-atlas-uri>
MONGODB_DB_NAME=hiresenseai
LLM_PROVIDER=groq
GROQ_MODEL=llama3-8b-8192
GROQ_API_KEY=<optional-free-tier-key>
HF_API_KEY=<optional-fallback-key>
VOSK_MODEL_PATH=
ALLOW_ONLINE_SPEECH_RECOGNITION=False
```

Build command:

```bash
pip install -r requirements.txt && python backend/manage.py collectstatic --noinput && python backend/manage.py migrate
```

Start command:

```bash
gunicorn backend.wsgi:application --chdir backend
```

`render.yaml` and `Procfile` are included for deployment compatibility.

## Offline Speech Deployment

Vosk package support is installed through `vosk==0.3.45`, but Vosk model files are not committed. For local production-like transcription:

1. Download a small Vosk model such as an English small model.
2. Extract it outside source control, for example `C:\Users\patel\models\vosk-model-small-en-us`.
3. Set:

```text
VOSK_MODEL_PATH=C:\Users\patel\models\vosk-model-small-en-us
ALLOW_ONLINE_SPEECH_RECOGNITION=False
```

If no offline model is configured, `/api/speech/transcribe/` returns `transcription_unavailable` instead of crashing or silently depending on the internet.

## Deployment Debugging

- If admin login fails, run migrations and recreate the superuser.
- If MongoDB pages fail, verify `MONGODB_URI`, Atlas network access, username, password, and database name.
- If webcam fails locally, check Windows camera permission and try `--camera 1`.
- If hosted webcam is needed, add browser-side capture and frame upload/streaming; hosted servers cannot open a local user webcam.
- If offline transcription is unavailable, verify `vosk` is installed and `VOSK_MODEL_PATH` points to an extracted model directory.
