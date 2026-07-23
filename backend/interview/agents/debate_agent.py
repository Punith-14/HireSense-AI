"""Debate-mode follow-up agent.

A "small intelligent behavior": after a normal question, the interviewer pushes
back on the candidate's own answer with one sharp, contrarian challenge to
create realistic pressure — instead of asking a generic follow-up.
"""

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.8,
        )
    return _llm


def generate_debate_question(question, answer, role="the candidate"):
    """Return one challenging counter-question about the candidate's answer.

    Returns an empty string on failure so callers can fall back gracefully.
    """
    answer = (answer or "").strip()
    if not answer:
        return ""

    prompt = f"""
    You are a sharp but respectful interviewer running a DEBATE-style pressure round
    for a {role}.

    They were asked:
    {question}

    They answered:
    {answer}

    Push back with EXACTLY ONE challenging follow-up that pressure-tests their answer.
    Rules:
    - Take a contrarian or devil's-advocate stance, or surface a trade-off they ignored.
    - Force them to defend, justify, or reconsider their position.
    - Be specific to what they actually said — quote or reference their point.
    - Keep it short and conversational. Do NOT ask them to write code.
    - Return ONLY the question. No preamble, headings, or explanation.
    """

    try:
        return get_llm().invoke(prompt).content.strip()
    except Exception as exc:
        print(f"Debate question error: {exc}")
        return ""
