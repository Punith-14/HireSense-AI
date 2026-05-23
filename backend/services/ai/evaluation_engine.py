import re

from services.ai import prompt_engine
from services.ai.adaptive_engine import AdaptiveEngine
from services.ai.llm_service import get_llm_service
from services.confidence_engine import ConfidenceEngine
from services.speech.speech_metrics import calculate_speech_metrics


FILLER_WORDS = {"um", "uh", "like", "actually", "basically", "you know", "sort of", "kind of"}


class EvaluationEngine:
    def __init__(self):
        self.llm = get_llm_service()
        self.adaptive = AdaptiveEngine()
        self.confidence = ConfidenceEngine()

    def evaluate(self, context):
        heuristic = self._heuristic_evaluation(context)
        prompt = prompt_engine.evaluation_prompt(context)

        def fallback():
            return heuristic

        model_result = self.llm.generate_json(prompt, fallback=fallback)
        merged = self._normalize({**heuristic, **model_result})
        adaptive = self.adaptive.decide(merged, context.get("difficulty", "medium"))
        
        is_adaptive_on = context.get("adaptive_mode", True)
        merged["next_difficulty"] = adaptive["next_difficulty"] if is_adaptive_on else context.get("difficulty", "medium")
        merged["adaptive_action"] = adaptive["adaptive_action"] if is_adaptive_on else "stabilize"
        merged["follow_up_recommended"] = adaptive["follow_up_recommended"]
        merged["pressure_level"] = adaptive["pressure_level"]
        return merged

    def _heuristic_evaluation(self, context):
        answer = context.get("answer_text", "") or ""
        speech = context.get("speech_metrics") or {}
        vision = context.get("vision_metrics") or {}
        skills = [skill.lower() for skill in context.get("skills", [])]

        words = re.findall(r"[A-Za-z0-9+#.]+", answer.lower())
        word_count = len(words)
        unique_words = len(set(words))
        skill_hits = sum(1 for skill in skills if any(part in answer.lower() for part in skill.split()))

        if "word_count" not in speech:
            speech = {**calculate_speech_metrics(answer, speech.get("duration_seconds", 0), speech), **speech}
        confidence_metrics = self.confidence.calculate(speech, vision)

        filler_count = int(speech.get("filler_count", self._count_fillers(answer)))
        pause_count = int(speech.get("pause_count", 0) or 0)
        words_per_minute = float(speech.get("words_per_minute", self._estimate_wpm(word_count, speech)) or 0)

        technical = min(100, 35 + word_count * 1.1 + unique_words * 0.45 + skill_hits * 9)
        if word_count < 12:
            technical -= 18
        if "example" in words or "because" in words or "tradeoff" in words:
            technical += 6

        clarity = min(100, 45 + min(word_count, 80) * 0.45 - filler_count * 4 - pause_count * 2)
        if 95 <= words_per_minute <= 165:
            clarity += 8
        elif words_per_minute:
            clarity -= 6

        hesitation = min(100, speech.get("hesitation_score", filler_count * 10 + pause_count * 8 + max(0, 80 - word_count) * 0.3))
        confidence = confidence_metrics["confidence_score"]
        communication = min(100, max(0, max(clarity, confidence_metrics["communication_score"])))
        technical = min(100, max(0, technical))

        overall = (technical * 0.45) + (communication * 0.25) + (confidence * 0.2) + ((100 - hesitation) * 0.1)
        return {
            "technical_score": round(technical),
            "communication_score": round(communication),
            "confidence_score": round(confidence),
            "hesitation_score": round(hesitation),
            "nervousness_score": confidence_metrics["nervousness_score"],
            "overall_rating": self._rating(overall),
            "strengths": self._strengths(technical, communication, confidence),
            "weaknesses": self._weaknesses(technical, communication, hesitation),
            "answer_summary": self._summarize(answer),
            "next_difficulty": "medium",
        }

    def _normalize(self, result):
        for key in ("technical_score", "communication_score", "confidence_score", "hesitation_score"):
            try:
                result[key] = int(max(0, min(100, float(result.get(key, 0)))))
            except (TypeError, ValueError):
                result[key] = 0
        result.setdefault("overall_rating", self._rating(result["technical_score"]))
        result.setdefault("strengths", [])
        result.setdefault("weaknesses", [])
        result.setdefault("answer_summary", "")
        return result

    def _count_fillers(self, answer):
        lowered = answer.lower()
        return sum(len(re.findall(rf"\b{re.escape(word)}\b", lowered)) for word in FILLER_WORDS)

    def _estimate_wpm(self, word_count, speech):
        duration = float(speech.get("duration_seconds", 0) or 0)
        if duration <= 0:
            return 0
        return (word_count / duration) * 60

    def _eye_contact_score(self, vision):
        attention = (vision.get("attention") or "").lower()
        if attention == "direct":
            return 85
        if attention == "partial":
            return 58
        if attention == "away":
            return 25
        return 50

    def _rating(self, score):
        if score >= 85:
            return "Excellent"
        if score >= 70:
            return "Good"
        if score >= 55:
            return "Average"
        return "Needs Improvement"

    def _strengths(self, technical, communication, confidence):
        strengths = []
        if technical >= 70:
            strengths.append("Shows relevant technical understanding")
        if communication >= 70:
            strengths.append("Communicates with usable clarity")
        if confidence >= 70:
            strengths.append("Presents with steady confidence")
        return strengths or ["Provides a starting point for follow-up assessment"]

    def _weaknesses(self, technical, communication, hesitation):
        weaknesses = []
        if technical < 60:
            weaknesses.append("Needs more technical depth and concrete examples")
        if communication < 60:
            weaknesses.append("Answer structure needs improvement")
        if hesitation > 60:
            weaknesses.append("Hesitation or pauses reduced delivery confidence")
        return weaknesses

    def _summarize(self, answer):
        cleaned = " ".join(answer.split())
        return cleaned[:220]
