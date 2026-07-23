from django.core.management.base import BaseCommand

from services.ai.interview_engine import InterviewEngine
from services.speech.speech_service import SpeechService


class Command(BaseCommand):
    help = "Run a backend-only adaptive interview loop from the terminal."

    def add_arguments(self, parser):
        parser.add_argument("--role", default="Python Developer")
        parser.add_argument("--mode", default="technical")
        parser.add_argument("--email", default=None)
        parser.add_argument("--turns", type=int, default=3)

    def handle(self, *args, **options):
        engine = InterviewEngine()
        speech = SpeechService()
        result = engine.start(options["role"], options["mode"], user_email=options["email"])
        session_id = result["session_id"]
        self.stdout.write(f"Session: {session_id}")
        self.stdout.write(f"Q1: {result['question']['question']}")

        for turn in range(options["turns"]):
            answer = input("Answer text: ").strip()
            if not answer:
                self.stdout.write("Empty answer received. Stopping.")
                break
            speech_metrics = speech.analyze_text(answer)
            response = engine.answer(session_id, answer, speech_metrics=speech_metrics, vision_metrics={})
            evaluation = response["evaluation"]
            self.stdout.write(
                "Scores: "
                f"technical={evaluation['technical_score']} "
                f"communication={evaluation['communication_score']} "
                f"confidence={evaluation['confidence_score']} "
                f"hesitation={evaluation['hesitation_score']}"
            )
            self.stdout.write(f"Next: {response['next_question']['question']}")

        report = engine.report(session_id)
        self.stdout.write(self.style.SUCCESS(f"Report generated: {report['report_id']}"))
