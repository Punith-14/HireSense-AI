from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

from .services.interview_router import (
    VALID_INTERVIEW_TYPES,
    evaluate_answer_by_type,
    generate_question_by_type,
    is_valid_interview_type,
    normalize_interview_type
)


@api_view(['GET', 'POST'])
def generate_question(request):

    if request.method == "GET":

        interview_type = "technical"
        role = "Java Developer"
        difficulty = "medium"
        topic = "general"

    else:

        interview_type = request.data.get("interview_type", "technical")
        role = request.data.get("role", "Java Developer")
        difficulty = request.data.get("difficulty", "medium")
        topic = request.data.get("topic", "general")

    interview_type = normalize_interview_type(interview_type)

    if not is_valid_interview_type(interview_type):
        return Response({
            "error": "Invalid interview_type",
            "valid_interview_types": VALID_INTERVIEW_TYPES
        }, status=400)

    result = generate_question_by_type(
        interview_type,
        role,
        difficulty,
        topic
    )

    return Response(result)


@api_view(['POST'])
def evaluate_response(request):

    interview_type = request.data.get("interview_type", "technical")
    question = request.data.get("question")
    answer = request.data.get("answer")

    interview_type = normalize_interview_type(interview_type)

    if not is_valid_interview_type(interview_type):
        return Response({
            "error": "Invalid interview_type",
            "valid_interview_types": VALID_INTERVIEW_TYPES
        }, status=400)

    if not question or not answer:
        return Response({
            "error": "question and answer are required"
        }, status=400)

    result = evaluate_answer_by_type(
        interview_type,
        question,
        answer
    )

    return Response(result)


# ==========================================
# PERSON 2 ENDPOINTS
# ==========================================
from mongoengine import DoesNotExist, ValidationError
from rest_framework import status
from services.ai.interview_engine import InterviewEngine
from services.speech.speech_service import SpeechService


def _engine():
    return InterviewEngine()


def _core_start_interview(request, forced_mode=None):
    role = (request.data.get("role") or "").strip()
    mode = forced_mode or (request.data.get("mode") or "technical").strip().lower()
    difficulty = (request.data.get("difficulty") or "medium").strip().lower()
    adaptive_mode = request.data.get("adaptive_mode", True)
    if isinstance(adaptive_mode, str):
        adaptive_mode = adaptive_mode.lower() == "true"
    user_email = (request.data.get("user_email") or "").strip() or None
    full_name = (request.data.get("full_name") or "").strip() or None

    # Prefer the authenticated user over any client-supplied identity, so a
    # session is always tied to the real, token-verified account.
    auth_user = getattr(request, "user", None)
    if auth_user is not None and getattr(auth_user, "is_authenticated", False):
        user_email = getattr(auth_user, "email", None) or user_email
        full_name = getattr(auth_user, "full_name", None) or full_name

    if not role:
        return Response({"error": "role is required"}, status=status.HTTP_400_BAD_REQUEST)
    if mode not in {"technical", "hr", "mixed", "behavioral"}:
        return Response({"error": "mode must be technical, hr, behavioral, or mixed"}, status=status.HTTP_400_BAD_REQUEST)

    return Response(_engine().start(role=role, mode=mode, difficulty=difficulty, adaptive_mode=adaptive_mode, user_email=user_email, full_name=full_name))

@api_view(["POST"])
def start_interview(request):
    return _core_start_interview(request)


def _parse_json_field(data):
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {}
    return data or {}

def _core_submit_answer(request):
    session_id = (request.data.get("session_id") or "").strip()
    answer_text = (request.data.get("answer_text") or "").strip()
    speech_metrics = _parse_json_field(request.data.get("speech_metrics"))
    vision_metrics = _parse_json_field(request.data.get("vision_metrics"))
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
def submit_answer(request):
    return _core_submit_answer(request)


@api_view(["POST"])
def evaluate_answer(request):
    session_id = (request.data.get("session_id") or "").strip()
    answer_text = (request.data.get("answer_text") or "").strip()
    speech_metrics = _parse_json_field(request.data.get("speech_metrics"))
    vision_metrics = _parse_json_field(request.data.get("vision_metrics"))

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

@api_view(["GET"])
def interview_history(request):
    from utils.mongo_documents import Report, UserProfile

    # Scope history to the authenticated user only (never leak other users' reports).
    auth_user = getattr(request, "user", None)
    profile = None
    if auth_user is not None and getattr(auth_user, "is_authenticated", False):
        profile = UserProfile.objects(email=auth_user.email).first()
    if profile is None:
        return Response({"history": []})

    reports = Report.objects(user=profile).order_by("-created_at")[:50]
    data = []
    for r in reports:
        session = r.interview.session if r.interview and r.interview.session else None
        data.append({
            "session_id": str(session.id) if session else None,
            "date": r.created_at.isoformat() if r.created_at else None,
            "role": r.role,
            "mode": r.mode,
            "agent_type": (r.mode.capitalize() if getattr(r, "mode", None) else (r.role or "").capitalize()),
            "score": r.final_score,
            "technical_score": r.technical_score,
            "communication_score": r.communication_score,
            "confidence_score": r.confidence_score,
            "recommendation": r.hiring_recommendation,
        })
    return Response({"history": data})

# --- Specific Wrappers for Checklist Compliance ---

@api_view(["POST"])
def generate_hr_question(request):
    return _core_start_interview(request, forced_mode="hr")

@api_view(["POST"])
def evaluate_hr_response(request):
    return _core_submit_answer(request)

@api_view(["POST"])
def generate_behavioral_question(request):
    return _core_start_interview(request, forced_mode="behavioral")

@api_view(["POST"])
def evaluate_behavioral_response(request):
    return _core_submit_answer(request)
