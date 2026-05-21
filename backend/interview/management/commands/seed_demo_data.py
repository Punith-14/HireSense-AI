from django.core.management.base import BaseCommand

from config.db import connect_mongodb
from utils.mongo_documents import Interview, InterviewSession, Report, UserProfile


class Command(BaseCommand):
    help = "Seed deterministic HireSenseAI demo data into MongoDB."

    def handle(self, *args, **options):
        connect_mongodb()

        user = UserProfile.objects(email="demo.candidate@hiresense.ai").modify(
            upsert=True,
            new=True,
            set__full_name="Demo Candidate",
            set__auth_provider="local-demo",
            set__profile={"role_target": "Backend Engineer", "experience_level": "mid"},
        )

        session = InterviewSession.objects(session_key="local-demo-session").modify(
            upsert=True,
            new=True,
            set__user=user,
            set__role="Backend Engineer",
            set__mode="technical",
            set__difficulty="medium",
            set__status="completed",
            set__runtime_metadata={"source": "seed_demo_data", "webcam_mode": "local"},
        )

        interview = Interview.objects(session=session).modify(
            upsert=True,
            new=True,
            set__user=user,
            set__role="Backend Engineer",
            set__mode="technical",
            set__questions=[
                {"question": "Explain how you would design a scalable interview scoring API.", "difficulty": "medium"},
                {"question": "How would you prevent duplicate report generation?", "difficulty": "medium"},
            ],
            set__transcript=[
                {"speaker": "candidate", "text": "I would use idempotent report generation keyed by session."}
            ],
            set__scores={
                "confidence": 82,
                "behavior": 78,
                "communication": 84,
                "technical": 80,
                "final": 81,
            },
            set__ai_feedback={"summary": "Strong backend reasoning with clear deployment awareness."},
        )

        Report.objects(interview=interview).modify(
            upsert=True,
            new=True,
            set__user=user,
            set__role="Backend Engineer",
            set__final_analysis={"summary": "Demo report for local admin verification."},
            set__recommendations=["Improve answer structure", "Add more concrete system metrics"],
            set__confidence_score=82,
            set__behavior_score=78,
            set__communication_score=84,
            set__technical_score=80,
            set__final_score=81,
            set__dominant_emotion="neutral",
            set__hiring_recommendation="proceed",
        )

        self.stdout.write(self.style.SUCCESS("Seeded HireSenseAI demo data in MongoDB."))
