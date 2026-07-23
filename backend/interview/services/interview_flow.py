from services.evaluator import evaluate_answer
from services.adaptive_logic import get_next_difficulty


def evaluate_interview_round(question, answer):

    # Step 1 — Evaluate Answer
    evaluation = evaluate_answer(question, answer)

    # Step 2 — Adaptive Difficulty
    next_difficulty = get_next_difficulty(
        evaluation["technical_score"]
    )

    return {
        "question": question,
        "evaluation": evaluation,
        "next_difficulty": next_difficulty
    }