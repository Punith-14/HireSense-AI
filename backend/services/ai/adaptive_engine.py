DIFFICULTY_ORDER = ["easy", "medium", "hard"]


class AdaptiveEngine:
    def decide(self, evaluation, current_difficulty):
        technical = float(evaluation.get("technical_score", 0))
        communication = float(evaluation.get("communication_score", 0))
        confidence = float(evaluation.get("confidence_score", 0))
        hesitation = float(evaluation.get("hesitation_score", 0))
        current_index = DIFFICULTY_ORDER.index(current_difficulty) if current_difficulty in DIFFICULTY_ORDER else 1

        strong = technical >= 78 and communication >= 70 and confidence >= 70 and hesitation <= 45
        weak = technical < 50 or communication < 45 or hesitation >= 75

        if strong:
            next_index = min(current_index + 1, len(DIFFICULTY_ORDER) - 1)
            action = "increase_depth"
            follow_up = True
        elif weak:
            next_index = max(current_index - 1, 0)
            action = "reduce_complexity"
            follow_up = technical >= 45
        else:
            next_index = current_index
            action = "stabilize"
            follow_up = True

        return {
            "next_difficulty": DIFFICULTY_ORDER[next_index],
            "adaptive_action": action,
            "follow_up_recommended": follow_up,
            "pressure_level": self._pressure_level(confidence, hesitation),
        }

    def _pressure_level(self, confidence, hesitation):
        if confidence >= 75 and hesitation <= 40:
            return "challenging"
        if confidence < 45 or hesitation > 70:
            return "supportive"
        return "balanced"
