from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
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
        _llm_evaluator = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="deepseek/deepseek-r1:free",
            temperature=0.3
        )
    return _llm_evaluator


# Behavioral Interview Agent — Question Generator
def generate_behavioral_question(topic="general"):

    prompt = f"""
    You are an experienced behavioral interviewer.

    Generate exactly ONE concise behavioral interview question focused on: {topic}.

    Topics can include: teamwork, leadership, conflict resolution, problem-solving, communication.

    Rules:
    - Keep question short and clear
    - Use the STAR method style (Situation, Task, Action, Result)
    - Make it realistic
    - Do not give explanation
    - Do not add headings
    - Do not add bullet points
    - Do not add answers

    Examples:
    - Tell me about a time you worked in a difficult team.
    - Describe a situation where you showed leadership under pressure.
    - Give an example of how you resolved a conflict with a colleague.
    """

    try:
        response = get_llm_question().invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"


# Behavioral Interview Agent — Answer Evaluator
def evaluate_behavioral_answer(question, answer):

    prompt = f"""
    You are an experienced behavioral interviewer.

    Question:
    {question}

    Candidate Answer:
    {answer}

    Evaluate the behavioral answer.

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
        response = get_llm_evaluator().invoke(prompt)

        cleaned_response = response.content.replace(
            "```json", ""
        ).replace(
            "```", ""
        ).strip()

        return json.loads(cleaned_response)
    except Exception as e:
        return f"Error: {str(e)}"
