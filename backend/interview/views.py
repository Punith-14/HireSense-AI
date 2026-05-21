from mongoengine import DoesNotExist, ValidationError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from services.ai.interview_engine import InterviewEngine
from services.speech.speech_service import SpeechService


def _engine():
    return InterviewEngine()


@api_view(["POST"])
def start_interview(request):
    role = (request.data.get("role") or "").strip()
    mode = (request.data.get("mode") or "technical").strip().lower()
    user_email = (request.data.get("user_email") or "").strip() or None
    full_name = (request.data.get("full_name") or "").strip() or None

    if not role:
        return Response({"error": "role is required"}, status=status.HTTP_400_BAD_REQUEST)
    if mode not in {"technical", "hr", "mixed"}:
        return Response({"error": "mode must be technical, hr, or mixed"}, status=status.HTTP_400_BAD_REQUEST)

    return Response(_engine().start(role=role, mode=mode, user_email=user_email, full_name=full_name))


@api_view(["POST"])
def submit_answer(request):
    session_id = (request.data.get("session_id") or "").strip()
    answer_text = (request.data.get("answer_text") or "").strip()
    speech_metrics = request.data.get("speech_metrics") or {}
    vision_metrics = request.data.get("vision_metrics") or {}
    audio_file = request.FILES.get("audio_file")

    if not session_id:
        return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not answer_text and audio_file:
        speech_result = SpeechService().transcribe_uploaded_file(audio_file)
        answer_text = speech_result.get("transcript", "")
        speech_metrics = {**speech_result.get("metrics", {}), **speech_metrics}
        if not answer_text:
            return Response(speech_result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if not answer_text:
        return Response({"error": "answer_text or audio_file is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        return Response(
            _engine().answer(
                session_id=session_id,
                answer_text=answer_text,
                speech_metrics=speech_metrics,
                vision_metrics=vision_metrics,
            )
        )
    except (DoesNotExist, ValidationError):
        return Response({"error": "interview session not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def evaluate_answer(request):
    session_id = (request.data.get("session_id") or "").strip()
    answer_text = (request.data.get("answer_text") or "").strip()
    speech_metrics = request.data.get("speech_metrics") or {}
    vision_metrics = request.data.get("vision_metrics") or {}

    if not session_id:
        return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not answer_text:
        return Response({"error": "answer_text is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        return Response(
            _engine().evaluate_only(
                session_id=session_id,
                answer_text=answer_text,
                speech_metrics=speech_metrics,
                vision_metrics=vision_metrics,
            )
        )
    except (DoesNotExist, ValidationError):
        return Response({"error": "interview session not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def interview_report(request):
    session_id = (request.query_params.get("session_id") or "").strip()
    if not session_id:
        return Response({"error": "session_id query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        return Response(_engine().report(session_id=session_id))
    except (DoesNotExist, ValidationError):
        return Response({"error": "interview session not found"}, status=status.HTTP_404_NOT_FOUND)
