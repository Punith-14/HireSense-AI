from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

_llm_question = None
_llm_evaluator = None

def get_llm_question():
    global _llm_question
    if _llm_question is None:
        _llm_question = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )
    return _llm_question

def get_llm_evaluator():
    global _llm_evaluator
    if _llm_evaluator is None:
        _llm_evaluator = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3
        )
    return _llm_evaluator


# HR Interview Agent — Question Generator
def generate_hr_question(role):

    prompt = f"""
    You are an experienced HR interviewer.

    Generate exactly ONE concise HR interview question for a {role} candidate.

    Rules:
    - Keep question short and clear
    - Make it realistic and professional
    - Focus on personality, motivation, or background
    - Do not give explanation
    - Do not add headings
    - Do not add bullet points
    - Do not add answers

    Examples of HR questions:
    - Tell me about yourself.
    - Why do you want to work here?
    - Where do you see yourself in 5 years?
    """

    try:
        response = get_llm_question().invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"


# HR Interview Agent — Answer Evaluator
def evaluate_hr_answer(question, answer):

    prompt = f"""
    You are an experienced HR interviewer.

    Question:
    {question}

    Candidate Answer:
    {answer}

    Evaluate the HR answer.

    Return ONLY valid JSON.

    Format:
    {{
        "communication_score": number,
        "confidence_score": number,
        "feedback": "short feedback",
        "followup_question": "one short follow-up HR question"
    }}

    Rules:
    - Scores out of 100
    - Follow-up question must be short and HR-focused
    - No markdown
    """

    try:
        response = get_llm_evaluator().invoke(prompt)

        cleaned_response = response.content.replace(
            "```json", ""
        ).replace(
            "```", ""
        ).strip()

        return json.loads(cleaned_response)
    except Exception as e:
        print(f"HR Evaluation Error: {str(e)}")
        return {
            "communication_score": 0,
            "confidence_score": 0,
            "feedback": "An error occurred during HR evaluation.",
            "followup_question": "Can you elaborate further?"
        }
