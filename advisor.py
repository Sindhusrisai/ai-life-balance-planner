# advisor.py
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def _init_genai():
    try:
        import google.generativeai as genai
    except Exception as e:
        raise RuntimeError("google-generativeai not installed or import failed") from e
    genai.configure(api_key=GEMINI_KEY)
    return genai

def ask_llm(prompt, max_tokens=300):
    if not GEMINI_KEY:
        return "LLM key not found. Please add GEMINI_API_KEY to .env"
    genai = _init_genai()
    model = genai.GenerativeModel("gemini-pro")
    resp = model.generate_content(prompt, max_output_tokens=max_tokens)
    return resp.text

def generate_advice(user_profile, day_plan, energy_level):
    tasks_text = "\n".join([f"- {p['title']} ({p['minutes']} min)" for p in day_plan])
    prompt = f"""
You are an empathetic productivity & wellness coach.
User profile: {user_profile}
Energy level today: {energy_level}
Today's planned items:
{tasks_text}

Give:
1) A one-line prioritized tip for this user.
2) Two micro-break activities (30-90 seconds).
3) One hydration/nutrition tip.
4) If any task seems too long for today, suggest deferring (1 short sentence).

Keep each item short and actionable.
"""
    return ask_llm(prompt)
