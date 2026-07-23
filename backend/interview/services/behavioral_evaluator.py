from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
import re

# Load env variables
load_dotenv()

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3
        )
    return _llm

def evaluate_behavioral_answer(question, answer):

    prompt = f"""
    You are an experienced behavioral interviewer.

    Question:
    {question}

    Candidate Answer:
    {answer}

    Evaluate the answer.

    Return ONLY valid JSON.

    Format:
    {{
        "teamwork_score": number,
        "leadership_score": number,
        "communication_score": number,
        "feedback": "short feedback",
        "followup_question": "one short follow-up behavioral question"
    }}

    Rules:
    - Scores out of 100
    - Follow-up question must be short and behavioral-focused
    - Evaluate based on clarity, structure, and real-world applicability
    - No markdown
    """
    try:
        response = get_llm().invoke(prompt)

        content = response.content
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {
            "teamwork_score": 0,
            "leadership_score": 0,
            "communication_score": 0,
            "feedback": "Could not parse the evaluation. Please try again.",
            "followup_question": "Can you elaborate on your answer?"
        }
    except Exception as e:
        print(f"Behavioral Evaluation Error: {str(e)}")
        return {
            "teamwork_score": 0,
            "leadership_score": 0,
            "communication_score": 0,
            "feedback": "An error occurred during Behavioral evaluation (API limit).",
            "followup_question": "Can you elaborate on your answer?"
        }
