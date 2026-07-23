import hashlib

from services.ai import prompt_engine
from services.ai.memory_engine import MemoryEngine
from services.ai.llm_service import get_llm_service
from services.confidence_engine import ConfidenceEngine
from interview.agents.debate_agent import generate_debate_question
from interview.services.interview_router import generate_question_by_type, evaluate_answer_by_type

class InterviewEngine:
    # Number of answered questions after which the interview is considered complete.
    MAX_QUESTIONS = 5

    def __init__(self):
        self.llm = get_llm_service()
        self.memory = MemoryEngine()

    def start(self, role, mode="technical", difficulty="medium", adaptive_mode=True, user_email=None, full_name=None):
        session, interview = self.memory.start_session(role=role, mode=mode, difficulty=difficulty, adaptive_mode=adaptive_mode, user_email=user_email, full_name=full_name)
        question = self._generate_question(session, interview)
        self.memory.append_question(interview, question)
        return {
            "session_id": str(session.id),
            "interview_id": str(interview.id),
            "role": role,
            "mode": mode,
            "question": question,
        }

    def answer(self, session_id, answer_text, speech_metrics=None, vision_metrics=None):
        session, interview = self.memory.get_interview(session_id)
        if not interview.questions:
            question = self._generate_question(session, interview)
            self.memory.append_question(interview, question)
        current_question = interview.questions[-1]

        evaluation_payload = evaluate_answer_by_type(session.mode, current_question.get("question"), answer_text)
        evaluation = evaluation_payload.get("result", {})
        evaluation["next_difficulty"] = evaluation_payload.get("next_difficulty", session.difficulty)

        # Fuse real delivery signals (pauses, speech speed, filler words, eye
        # contact) into a measured confidence score, replacing the LLM's guess.
        signals = self._confidence_signals(speech_metrics, vision_metrics)
        if signals:
            evaluation.update(signals)

        self.memory.append_answer(
            interview,
            {
                "question": current_question.get("question"),
                "answer_text": answer_text,
                "speech_metrics": speech_metrics or {},
                "vision_metrics": vision_metrics or {},
                "answer_summary": evaluation.get("answer_summary"),
                "evaluation": evaluation,
            },
        )
        self.memory.update_after_evaluation(session, interview, evaluation)

        answered = len(interview.transcript or [])
        is_complete = answered >= self.MAX_QUESTIONS

        next_question = None
        if not is_complete:
            next_question = self._generate_follow_up_or_next(session, interview, answer_text, current_question, evaluation)
            self.memory.append_question(interview, next_question)

        return {
            "session_id": str(session.id),
            "evaluation": evaluation,
            "next_question": next_question,
            "is_complete": is_complete,
            "questions_answered": answered,
        }

    def evaluate_only(self, session_id, answer_text, speech_metrics=None, vision_metrics=None):
        session, interview = self.memory.get_interview(session_id)
        current_question = interview.questions[-1] if interview.questions else {"question": "", "difficulty": session.difficulty}
        evaluation_payload = evaluate_answer_by_type(session.mode, current_question.get("question"), answer_text)
        return evaluation_payload.get("result", {})

    def report(self, session_id):
        session, interview = self.memory.get_interview(session_id)
        context = {
            "role": session.role,
            "mode": session.mode,
            "questions": interview.questions or [],
            "transcript": interview.transcript or [],
            "scores": interview.scores or {},
        }
        prompt = prompt_engine.report_prompt(context)
        payload = self.llm.generate_json(prompt, fallback=lambda: self._fallback_report(context))
        report = self.memory.finish_report(session, interview, payload)
        return {
            "session_id": str(session.id),
            "report_id": str(report.id),
            "report": {
                "final_analysis": report.final_analysis,
                "recommendations": report.recommendations,
                "confidence_score": report.confidence_score,
                "behavior_score": report.behavior_score,
                "communication_score": report.communication_score,
                "technical_score": report.technical_score,
                "final_score": report.final_score,
                "hiring_recommendation": report.hiring_recommendation,
            },
            "transcript": interview.transcript or [],
            "questions": interview.questions or []
        }

    def _generate_question(self, session, interview):
        result = generate_question_by_type(session.mode, session.role, session.difficulty, "general")
        return {
            "question": result.get("question", ""),
            "difficulty": result.get("difficulty", "medium"),
            "category": session.mode,
            "expected_skills": [],
            "follow_up_enabled": False,
            "interviewer_intent": ""
        }

    def _confidence_signals(self, speech_metrics, vision_metrics):
        """Compute a measured confidence score from real delivery signals.

        Returns None when there is nothing to measure (e.g. a typed answer with
        no webcam), so we never fabricate a confidence number from thin air.
        """
        speech = speech_metrics or {}
        vision = vision_metrics or {}
        has_speech = bool(speech.get("word_count") or speech.get("duration_seconds"))
        has_vision = (vision.get("attention") or "").lower() in ("direct", "partial", "away")
        if not (has_speech or has_vision):
            return None

        result = ConfidenceEngine().calculate(speech, vision)
        return {
            "confidence_score": result["confidence_score"],
            "eye_contact_score": result["eye_contact_score"],
            "nervousness_score": result["nervousness_score"],
        }

    def _generate_follow_up_or_next(self, session, interview, answer_text, current_question, evaluation):
        # DEBATE MODE: after a normal question, challenge the candidate's own
        # answer once to create realistic pressure. After that debate turn, move
        # on to a fresh adaptive question so we don't loop forever.
        already_challenged = (current_question.get("category") or "").endswith("debate")
        if not already_challenged and (answer_text or "").strip():
            debate_q = generate_debate_question(
                current_question.get("question", ""), answer_text, session.role
            )
            if not debate_q:
                debate_q = evaluation.get("followup_question")  # graceful fallback
            if debate_q:
                return {
                    "question": debate_q,
                    "difficulty": session.difficulty,
                    "category": f"{session.mode}_debate",
                    "expected_skills": [],
                    "follow_up_enabled": False,
                    "interviewer_intent": "Challenge and pressure-test the candidate's answer.",
                }

        session.difficulty = evaluation.get("next_difficulty", session.difficulty)
        return self._generate_question(session, interview)

    def _normalize_question(self, question):
        expected = question.get("expected_skills") or []
        if isinstance(expected, str):
            expected = [expected]
        return {
            "question": str(question.get("question", "")).strip(),
            "difficulty": question.get("difficulty", "medium"),
            "category": question.get("category", "technical"),
            "expected_skills": expected,
            "follow_up_enabled": bool(question.get("follow_up_enabled", True)),
            "interviewer_intent": question.get("interviewer_intent", "Assess role-relevant depth."),
        }

    def _fallback_question(self, context):
        skills = context["skills"]
        previous = " ".join(context.get("previous_questions") or [])
        difficulty = context.get("difficulty", "medium")
        skill = self._select_skill(skills, previous)
        depth = {
            "easy": "explain the core idea of",
            "medium": "walk through how you would use",
            "hard": "design a production-grade approach involving",
        }.get(difficulty, "walk through how you would use")
        return {
            "question": f"For a {context['role']} role, {depth} {skill} in a real project. Include tradeoffs and failure cases.",
            "difficulty": difficulty,
            "category": context.get("mode", "technical"),
            "expected_skills": [skill],
            "follow_up_enabled": True,
            "interviewer_intent": f"Assess practical depth in {skill}.",
        }

    def _fallback_follow_up(self, context):
        answer = context.get("answer_text", "")
        fingerprint = hashlib.sha1(answer.encode("utf-8")).hexdigest()
        angle = ["performance", "failure handling", "testing", "scalability"][int(fingerprint[:2], 16) % 4]
        return {
            "question": f"You mentioned that approach. How would you handle {angle} if this had to run in production under real user traffic?",
            "difficulty": context.get("next_difficulty", "medium"),
            "category": "technical_follow_up",
            "expected_skills": [angle],
            "follow_up_enabled": True,
            "interviewer_intent": f"Probe contextual {angle} depth based on the previous answer.",
        }

    def _fallback_report(self, context):
        scores = context.get("scores") or {}
        final = float(scores.get("final", 0) or 0)
        if final >= 80:
            recommendation = "proceed"
        elif final >= 60:
            recommendation = "borderline"
        else:
            recommendation = "do_not_proceed"
        return {
            "summary": f"Candidate completed a {context['mode']} interview for {context['role']}.",
            "strengths": ["Answered role-relevant questions", "Provided enough signal for scoring"],
            "weaknesses": ["Needs deeper evidence in weaker score areas"],
            "recommendations": ["Use concrete examples", "Structure answers with problem, approach, tradeoffs, result"],
            "hiring_recommendation": recommendation,
        }

    def _select_skill(self, skills, previous_text):
        lowered = previous_text.lower()
        for skill in skills:
            if skill.lower() not in lowered:
                return skill
        digest = hashlib.sha1(previous_text.encode("utf-8")).hexdigest()
        return skills[int(digest[:2], 16) % len(skills)]
