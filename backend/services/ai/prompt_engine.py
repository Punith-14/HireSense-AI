import json


ROLE_SKILLS = {
    "python developer": ["Python internals", "OOP", "REST APIs", "databases", "testing", "concurrency"],
    "java backend developer": ["Java", "Spring Boot", "JPA", "microservices", "SQL", "concurrency"],
    "mern stack developer": ["React", "Node.js", "Express", "MongoDB", "API design", "state management"],
    "data scientist": ["statistics", "machine learning", "feature engineering", "model evaluation", "Python", "SQL"],
}


def normalize_role(role):
    return " ".join((role or "software engineer").strip().lower().split())


def skills_for_role(role):
    normalized = normalize_role(role)
    if normalized in ROLE_SKILLS:
        return ROLE_SKILLS[normalized]

    tokens = [token for token in normalized.replace("-", " ").split() if len(token) > 2]
    inferred = []
    if "python" in tokens:
        inferred.extend(["Python", "OOP", "REST APIs", "testing"])
    if "java" in tokens:
        inferred.extend(["Java", "Spring Boot", "SQL", "concurrency"])
    if "data" in tokens or "scientist" in tokens:
        inferred.extend(["statistics", "machine learning", "model evaluation"])
    if "backend" in tokens:
        inferred.extend(["API design", "databases", "scalability"])
    if "developer" in tokens and not inferred:
        inferred.extend(["programming fundamentals", "debugging", "system design"])
    return list(dict.fromkeys(inferred or ["problem solving", "API design", "databases", "testing"]))


def question_prompt(context):
    payload = {
        "role": context["role"],
        "mode": context["mode"],
        "difficulty": context["difficulty"],
        "skills": context["skills"],
        "previous_questions": context["previous_questions"],
        "previous_answer_summary": context.get("previous_answer_summary"),
        "last_evaluation": context.get("last_evaluation"),
    }
    return (
        "You are a senior adaptive technical interviewer. Generate exactly one contextual interview question. "
        "Do not repeat previous questions. Return JSON only with keys: question, difficulty, category, "
        "expected_skills, follow_up_enabled, interviewer_intent.\n"
        f"Context:\n{json.dumps(payload, ensure_ascii=True)}"
    )


def evaluation_prompt(context):
    payload = {
        "role": context["role"],
        "question": context["question"],
        "answer": context["answer_text"],
        "difficulty": context["difficulty"],
        "speech_metrics": context["speech_metrics"],
        "vision_metrics": context["vision_metrics"],
        "skills": context["skills"],
    }
    return (
        "You are evaluating a mock interview answer. Score technical correctness, clarity, confidence, "
        "hesitation, and give a concise evidence-based critique. Return JSON only with keys: "
        "technical_score, communication_score, confidence_score, hesitation_score, overall_rating, "
        "strengths, weaknesses, next_difficulty, answer_summary.\n"
        f"Context:\n{json.dumps(payload, ensure_ascii=True)}"
    )


def follow_up_prompt(context):
    payload = {
        "role": context["role"],
        "question": context["question"],
        "answer": context["answer_text"],
        "evaluation": context["evaluation"],
        "next_difficulty": context["next_difficulty"],
    }
    return (
        "Generate one contextual follow-up interview question based on the candidate answer. "
        "It must probe a concrete gap or deepen a strong answer. Return JSON only with keys: "
        "question, difficulty, category, expected_skills, follow_up_enabled, interviewer_intent.\n"
        f"Context:\n{json.dumps(payload, ensure_ascii=True)}"
    )


def report_prompt(context):
    payload = {
        "role": context["role"],
        "mode": context["mode"],
        "questions": context["questions"],
        "transcript": context["transcript"],
        "scores": context["scores"],
    }
    return (
        "Create a final structured interview report. Return JSON only with keys: summary, strengths, "
        "weaknesses, recommendations, hiring_recommendation.\n"
        f"Context:\n{json.dumps(payload, ensure_ascii=True)}"
    )
