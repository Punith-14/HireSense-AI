from datetime import datetime, timezone

from mongoengine import (
    DateTimeField,
    DictField,
    Document,
    EmailField,
    FloatField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)


def utc_now():
    return datetime.now(timezone.utc)


class TimestampedDocument(Document):
    meta = {"abstract": True}

    created_at = DateTimeField(default=utc_now, required=True)
    updated_at = DateTimeField(default=utc_now, required=True)

    def save(self, *args, **kwargs):
        self.updated_at = utc_now()
        return super().save(*args, **kwargs)


class UserProfile(TimestampedDocument):
    meta = {
        "collection": "users",
        "indexes": [
            {"fields": ["email"], "unique": True},
            "created_at",
            "updated_at",
        ],
    }

    email = EmailField(required=True)
    full_name = StringField(max_length=180)
    auth_provider = StringField(default="django")
    profile = DictField(default=dict)
    interview_history = ListField(StringField(), default=list)

    def __str__(self):
        return self.email


class InterviewSession(TimestampedDocument):
    meta = {
        "collection": "sessions",
        "indexes": [
            "user",
            "status",
            "role",
            "created_at",
            {"fields": ["session_key"], "unique": True, "sparse": True},
        ],
    }

    user = ReferenceField(UserProfile)
    session_key = StringField()
    role = StringField(required=True)
    mode = StringField(default="technical")
    difficulty = StringField(default="medium")
    status = StringField(default="created")
    runtime_metadata = DictField(default=dict)

    def __str__(self):
        return f"{self.role} {self.status}"


class Interview(TimestampedDocument):
    meta = {
        "collection": "interviews",
        "indexes": [
            "user",
            "session",
            "role",
            "mode",
            "created_at",
            "scores.final",
        ],
    }

    user = ReferenceField(UserProfile)
    session = ReferenceField(InterviewSession)
    role = StringField(required=True)
    mode = StringField(default="technical")
    transcript = ListField(DictField(), default=list)
    questions = ListField(DictField(), default=list)
    scores = DictField(default=dict)
    ai_feedback = DictField(default=dict)

    def __str__(self):
        return f"{self.role} interview"


class Report(TimestampedDocument):
    meta = {
        "collection": "reports",
        "indexes": [
            "user",
            "interview",
            "role",
            "dominant_emotion",
            "created_at",
            "-final_score",
        ],
    }

    user = ReferenceField(UserProfile)
    interview = ReferenceField(Interview)
    role = StringField(required=True)
    final_analysis = DictField(default=dict)
    recommendations = ListField(StringField(), default=list)
    confidence_score = FloatField(default=0)
    behavior_score = FloatField(default=0)
    communication_score = FloatField(default=0)
    technical_score = FloatField(default=0)
    final_score = FloatField(default=0)
    dominant_emotion = StringField()
    hiring_recommendation = StringField()
    generated_version = IntField(default=1)

    def __str__(self):
        return f"{self.role} report {self.final_score}"
