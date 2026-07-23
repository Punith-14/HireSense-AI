from uuid import uuid4

from config.db import connect_mongodb
from utils.mongo_documents import Interview, InterviewSession, Report, UserProfile


class MemoryEngine:
    def __init__(self):
        connect_mongodb()

    def start_session(self, role, mode, difficulty="medium", adaptive_mode=True, user_email=None, full_name=None):
        user = None
        if user_email:
            user = UserProfile.objects(email=user_email).modify(
                upsert=True,
                new=True,
                set__full_name=full_name or "",
                set__auth_provider="local-api",
            )

        session = InterviewSession(
            user=user,
            session_key=str(uuid4()),
            role=role,
            mode=mode,
            difficulty=difficulty,
            adaptive_mode=adaptive_mode,
            status="active",
            runtime_metadata={
                "turn": 0,
                "last_evaluation": None,
                "skills_covered": [],
                "adaptive_history": [],
            },
        ).save()
        interview = Interview(user=user, session=session, role=role, mode=mode).save()
        return session, interview

    def get_interview(self, session_id):
        session = InterviewSession.objects.get(id=session_id)
        interview = Interview.objects.get(session=session)
        return session, interview

    def append_question(self, interview, question):
        questions = list(interview.questions or [])
        questions.append(question)
        interview.questions = questions
        interview.save()
        return question

    def append_answer(self, interview, answer_payload):
        transcript = list(interview.transcript or [])
        transcript.append(answer_payload)
        interview.transcript = transcript
        interview.save()

    def update_after_evaluation(self, session, interview, evaluation):
        metadata = dict(session.runtime_metadata or {})
        metadata["turn"] = int(metadata.get("turn", 0)) + 1
        metadata["last_evaluation"] = evaluation
        metadata.setdefault("adaptive_history", []).append(
            {
                "turn": metadata["turn"],
                "next_difficulty": evaluation.get("next_difficulty"),
                "adaptive_action": evaluation.get("adaptive_action"),
            }
        )
        session.runtime_metadata = metadata
        session.difficulty = evaluation.get("next_difficulty", session.difficulty)
        session.save()

        interview.scores = self._aggregate_scores(interview)
        interview.ai_feedback = evaluation
        interview.save()

    def build_context(self, session, interview):
        metadata = session.runtime_metadata or {}
        return {
            "role": session.role,
            "mode": session.mode,
            "difficulty": session.difficulty,
            "adaptive_mode": getattr(session, "adaptive_mode", True),
            "previous_questions": [item.get("question") for item in interview.questions or []],
            "previous_answer_summary": self._last_answer(interview),
            "last_evaluation": metadata.get("last_evaluation"),
        }

    def finish_report(self, session, interview, report_payload):
        session.status = "completed"
        session.save()
        scores = interview.scores or {}
        report = Report.objects(interview=interview).modify(
            upsert=True,
            new=True,
            set__user=interview.user,
            set__role=interview.role,
            set__mode=interview.mode,
            set__final_analysis=report_payload,
            set__recommendations=report_payload.get("recommendations", []),
            set__confidence_score=scores.get("confidence", 0),
            set__behavior_score=scores.get("teamwork", 0),
            set__communication_score=scores.get("communication", 0),
            set__technical_score=scores.get("technical", 0),
            set__final_score=scores.get("final", 0),
            set__dominant_emotion=report_payload.get("dominant_emotion"),
            set__hiring_recommendation=report_payload.get("hiring_recommendation"),
        )
        return report

    def _last_answer(self, interview):
        transcript = interview.transcript or []
        if not transcript:
            return None
        return transcript[-1].get("answer_summary") or transcript[-1].get("answer_text", "")[:220]

    # Metrics that count toward the overall final score (hesitation is diagnostic, not additive).
    SCORE_METRICS = ("technical", "communication", "confidence", "teamwork", "leadership")

    def _aggregate_scores(self, interview):
        """Average each metric across every answered question.

        Metrics that were never produced (e.g. teamwork in a purely technical
        interview) stay at 0 rather than being back-filled with fabricated
        defaults. The final score is the mean of the metrics that were actually
        measured, so a failed/empty evaluation yields 0 instead of a flattering
        placeholder.
        """
        buckets = {m: [] for m in (*self.SCORE_METRICS, "hesitation")}
        for entry in (interview.transcript or []):
            evaluation = entry.get("evaluation") or {}
            for metric in buckets:
                value = evaluation.get(f"{metric}_score")
                if isinstance(value, (int, float)):
                    buckets[metric].append(value)

        scores = {
            metric: round(sum(values) / len(values), 1) if values else 0
            for metric, values in buckets.items()
        }
        measured = [scores[m] for m in self.SCORE_METRICS if buckets[m]]
        scores["final"] = round(sum(measured) / len(measured), 1) if measured else 0
        return scores
