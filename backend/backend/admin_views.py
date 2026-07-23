from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from pymongo.errors import PyMongoError

from config.db import assert_mongodb_ready
from utils.mongo_documents import Interview, InterviewSession, Report, UserProfile


def _mongo_unavailable_context():
    ok, message = assert_mongodb_ready()
    if ok:
        return None
    return {
        "db_error": message,
        "db_fix": "Start MongoDB Server on localhost:27017 or set MONGO_URI in .env.",
    }


def _contains_filter(queryset, field, value):
    if value:
        return queryset.filter(**{f"{field}__icontains": value})
    return queryset


def _gte_filter(queryset, field, value):
    if not value:
        return queryset
    try:
        return queryset.filter(**{f"{field}__gte": float(value)})
    except ValueError:
        return queryset


@staff_member_required
def users_admin(request):
    search = request.GET.get("q", "").strip()
    db_context = _mongo_unavailable_context()
    users = []
    if not db_context:
        try:
            users = UserProfile.objects.order_by("-created_at")
            if search:
                users = users.filter(email__icontains=search)
            users = users[:200]
        except PyMongoError as exc:
            db_context = {"db_error": str(exc), "db_fix": "Verify MongoDB Server is running."}
    return render(
        request,
        "admin/hiresense/users.html",
        {"title": "HireSenseAI Users", "users": users, "search": search, **(db_context or {})},
    )


@staff_member_required
def sessions_admin(request):
    role = request.GET.get("role", "").strip()
    status = request.GET.get("status", "").strip()
    db_context = _mongo_unavailable_context()
    sessions = []
    if not db_context:
        try:
            sessions = InterviewSession.objects.order_by("-created_at")
            sessions = _contains_filter(sessions, "role", role)
            sessions = _contains_filter(sessions, "status", status)
            sessions = sessions[:200]
        except PyMongoError as exc:
            db_context = {"db_error": str(exc), "db_fix": "Verify MongoDB Server is running."}
    return render(
        request,
        "admin/hiresense/sessions.html",
        {
            "title": "HireSenseAI Sessions",
            "sessions": sessions,
            "role": role,
            "status": status,
            **(db_context or {}),
        },
    )


@staff_member_required
def interviews_admin(request):
    role = request.GET.get("role", "").strip()
    min_score = request.GET.get("min_score", "").strip()
    db_context = _mongo_unavailable_context()
    interviews = []
    if not db_context:
        try:
            interviews = Interview.objects.order_by("-created_at")
            interviews = _contains_filter(interviews, "role", role)
            interviews = _gte_filter(interviews, "scores__final", min_score)
            interviews = interviews[:200]
        except PyMongoError as exc:
            db_context = {"db_error": str(exc), "db_fix": "Verify MongoDB Server is running."}
    return render(
        request,
        "admin/hiresense/interviews.html",
        {
            "title": "HireSenseAI Interviews",
            "interviews": interviews,
            "role": role,
            "min_score": min_score,
            **(db_context or {}),
        },
    )


@staff_member_required
def reports_admin(request):
    role = request.GET.get("role", "").strip()
    emotion = request.GET.get("emotion", "").strip()
    min_score = request.GET.get("min_score", "").strip()
    db_context = _mongo_unavailable_context()
    reports = []
    if not db_context:
        try:
            reports = Report.objects.order_by("-created_at")
            reports = _contains_filter(reports, "role", role)
            reports = _contains_filter(reports, "dominant_emotion", emotion)
            reports = _gte_filter(reports, "final_score", min_score)
            reports = reports[:200]
        except PyMongoError as exc:
            db_context = {"db_error": str(exc), "db_fix": "Verify MongoDB Server is running."}
    return render(
        request,
        "admin/hiresense/reports.html",
        {
            "title": "HireSenseAI Reports",
            "reports": reports,
            "role": role,
            "emotion": emotion,
            "min_score": min_score,
            **(db_context or {}),
        },
    )
