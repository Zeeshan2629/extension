import os
from dotenv import load_dotenv

# Explicitly load the .env file from parent directory
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Check if the key is loaded
print("Gemini Key Loaded:", os.getenv("GEMINI_API_KEY") is not None)

from gemini_client import generate_answer

question = "Explain binary search in short."
print("\nGemini Response:")
print(generate_answer(question))
