class ConfidenceEngine:
    def calculate(self, speech_metrics=None, vision_metrics=None):
        speech = speech_metrics or {}
        vision = vision_metrics or {}
        hesitation = float(speech.get("hesitation_score", 0) or 0)
        filler_count = float(speech.get("filler_count", 0) or 0)
        pause_duration = float(speech.get("pause_duration_seconds", 0) or 0)
        wpm = float(speech.get("words_per_minute", 0) or 0)
        eye_contact = float(vision.get("eye_contact_score", self._eye_contact_from_attention(vision)) or 0)
        emotion_score = float(vision.get("emotion_score", 0.5) or 0.5)

        speed_penalty = 0
        if wpm and wpm < 90:
            speed_penalty = 8
        elif wpm > 180:
            speed_penalty = 10

        nervousness = min(100, hesitation + filler_count * 4 + pause_duration * 3 + speed_penalty)
        confidence = max(0, min(100, 58 + eye_contact * 0.25 + emotion_score * 18 - nervousness * 0.35))
        communication = speech.get("communication_score")
        if communication is None:
            communication = max(0, min(100, 76 - filler_count * 4 - pause_duration * 2 - speed_penalty))

        return {
            "confidence_score": round(confidence),
            "nervousness_score": round(nervousness),
            "communication_score": round(float(communication)),
            "eye_contact_score": round(eye_contact),
        }

    def _eye_contact_from_attention(self, vision):
        attention = (vision.get("attention") or "").lower()
        if attention == "direct":
            return 85
        if attention == "partial":
            return 58
        if attention == "away":
            return 25
        return 50
