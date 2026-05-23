from interview.agents.behavioral_agent import generate_behavioral_question
from interview.agents.hr_agent import generate_hr_question
from interview.agents.technical_agent import generate_technical_question
from interview.services.adaptive_logic import get_next_difficulty
from interview.services.behavioral_evaluator import evaluate_behavioral_answer
from interview.services.evaluator import evaluate_answer
from interview.services.hr_evaluator import evaluate_hr_answer


VALID_INTERVIEW_TYPES = ["technical", "hr", "behavioral"]


def normalize_interview_type(interview_type):
    return (interview_type or "technical").lower()


def is_valid_interview_type(interview_type):
    return interview_type in VALID_INTERVIEW_TYPES


def generate_question_by_type(
    interview_type,
    role="Java Developer",
    difficulty="medium",
    topic="general"
):
    interview_type = normalize_interview_type(interview_type)

    if interview_type == "hr":
        question = generate_hr_question(role)

    elif interview_type == "behavioral":
        question = generate_behavioral_question(topic)

    else:
        question = generate_technical_question(
            role,
            difficulty
        )

    return {
        "interview_type": interview_type,
        "role": role,
        "difficulty": difficulty,
        "topic": topic,
        "question": question
    }


def evaluate_answer_by_type(interview_type, question, answer):
    interview_type = normalize_interview_type(interview_type)
    response = {
        "interview_type": interview_type
    }

    if interview_type == "hr":
        result = evaluate_hr_answer(
            question,
            answer
        )

    elif interview_type == "behavioral":
        result = evaluate_behavioral_answer(
            question,
            answer
        )

    else:
        result = evaluate_answer(
            question,
            answer
        )
        response["next_difficulty"] = get_next_difficulty(
            result["technical_score"]
        )

    response["result"] = result

    return response
