import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- FORCE .env LOAD ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENV_PATH = os.path.join(BASE_DIR, '.env')

if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print(f"⚠️ .env not found at {ENV_PATH}")

# --- CONFIGURE GEMINI ---
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("⚠️ Gemini API key not found. Please set it in .env at project root.")

genai.configure(api_key=API_KEY)


def generate_answer(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the generated text.
    Tries gemini-2.5-flash first, then falls back to gemini-2.5-pro.
    """
    try:
        try:
            # 🧠 Fast model (free tier supported)
            model = genai.GenerativeModel("models/gemini-2.5-flash")
        except Exception:
            # 🧩 fallback if flash not found
            model = genai.GenerativeModel("models/gemini-2.5-pro")

        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else "[No response received from Gemini.]"

    except Exception as e:
        return f"[Gemini API error: {e}]"
