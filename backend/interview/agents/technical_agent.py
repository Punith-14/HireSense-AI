from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )
    return _llm

# Technical Interview Agent
def generate_technical_question(role, difficulty):

    prompt = f"""
    You are an experienced technical interviewer.

    Generate exactly ONE concise {difficulty}-level
    interview question for a {role} candidate.

    Rules:
    - Keep question short and conversational
    - Make it realistic to a verbal technical interview
    - CRITICAL: DO NOT ask the candidate to write code. Ask conceptual, architectural, or debugging questions instead.
    - Do not give explanation
    - Do not add headings
    - Do not add bullet points
    - Do not add answers
    """

    try:
        response = get_llm().invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"