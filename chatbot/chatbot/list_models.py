import os
from dotenv import load_dotenv
import google.generativeai as genai

# explicit .env load (project root)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

print("Using GEMINI_API_KEY:", bool(os.getenv("GEMINI_API_KEY")))

# list models
try:
    models = genai.list_models()
    print("Available models (names):")
    for m in models:
        # print name and a brief summary if available
        print("-", getattr(m, "name", repr(m)))
except Exception as e:
    print("Error listing models:", e)
