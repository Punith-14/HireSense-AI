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

        scores = dict(interview.scores or {})
        scores.update(
            {
                "technical": evaluation.get("technical_score", scores.get("technical", 0)),
                "communication": evaluation.get("communication_score", scores.get("communication", 0)),
                "confidence": evaluation.get("confidence_score", scores.get("confidence", 0)),
                "teamwork": evaluation.get("teamwork_score", scores.get("teamwork", 0)),
                "leadership": evaluation.get("leadership_score", scores.get("leadership", 0)),
                "hesitation": evaluation.get("hesitation_score", scores.get("hesitation", 0)),
                "final": self._final_score(evaluation),
            }
        )
        interview.scores = scores
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
            set__final_analysis=report_payload,
            set__recommendations=report_payload.get("recommendations", []),
            set__confidence_score=scores.get("confidence", 80),
            set__behavior_score=scores.get("teamwork", 85),
            set__communication_score=scores.get("communication", 75),
            set__technical_score=scores.get("technical", 80),
            set__final_score=scores.get("final", 80),
            set__dominant_emotion=report_payload.get("dominant_emotion"),
            set__hiring_recommendation=report_payload.get("hiring_recommendation"),
        )
        return report

    def _last_answer(self, interview):
        transcript = interview.transcript or []
        if not transcript:
            return None
        return transcript[-1].get("answer_summary") or transcript[-1].get("answer_text", "")[:220]

    def _final_score(self, evaluation):
        base = max([
            evaluation.get("technical_score", 0),
            evaluation.get("teamwork_score", 0),
            evaluation.get("communication_score", 0)
        ])
        return round(base, 1) if base > 0 else 75.0
