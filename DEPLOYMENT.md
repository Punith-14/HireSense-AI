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
mongodb://localhost:27017/hiresense_ai
```

`.env` values:

```text
MONGO_URI=mongodb://localhost:27017/hiresense_ai
MONGO_DB_NAME=hiresense_ai
```

The connection layer is `backend/config/db.py`. It supports local MongoDB now and MongoDB Atlas later by changing `MONGO_URI`.

## MongoDB Compass

Use the following values to connect and validate persistence:

1. **Connection URI:** `mongodb://localhost:27017/hiresense_ai` (or `MONGO_URI` from `.env`).
2. **Database name:** `hiresense_ai`.
3. **Collections:** `users`, `sessions`, `interviews`, `reports`.
4. **Inspect collections:** open the database in Compass, click a collection, and use the Documents tab to browse saved sessions/interviews.
5. **Verify persistence:** create a new interview session, refresh the collection, then restart MongoDB and confirm the same documents remain.
6. **Verify indexes:** open the Indexes tab per collection and confirm the unique `email` index for `users` plus the session key index for `sessions`.
7. **Debug failed connections:** ensure MongoDB is running, confirm `MONGO_URI` is correct, verify Atlas IP allowlist/credentials, and confirm the database name matches `MONGO_DB_NAME`.

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

## Realtime Interview Loop

Run a local end-to-end loop with microphone + webcam capture:

```powershell
.\venv\Scripts\python.exe backend\manage.py run_realtime_interview --role "Python Developer" --turns 3
```

## Render Free Tier

Set environment variables:

```text
DJANGO_SECRET_KEY=<strong-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<render-hostname>.onrender.com
MONGO_URI=<mongodb-atlas-uri>
MONGO_DB_NAME=hiresense_ai
LLM_PROVIDER=auto
XAI_MODEL=grok-2-latest
XAI_API_KEY=<xai-key>
HF_LOCAL_ENABLED=False
HF_MODEL=microsoft/Phi-3-mini-4k-instruct
VOSK_MODEL_PATH=
ALLOW_ONLINE_SPEECH_RECOGNITION=False
ONLINE_SPEECH_ENDPOINT=
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
- If MongoDB pages fail, verify `MONGO_URI`, Atlas network access, username, password, and database name.
- If webcam fails locally, check Windows camera permission and try `--camera 1`.
- If hosted webcam is needed, add browser-side capture and frame upload/streaming; hosted servers cannot open a local user webcam.
- If offline transcription is unavailable, verify `vosk` is installed and `VOSK_MODEL_PATH` points to an extracted model directory.
