import os
from dotenv import load_dotenv
from pathlib import Path

# Locate .env file
env_path = Path(__file__).resolve().parent / ".env"
print("Looking for .env at:", env_path)

# Try loading it
load_dotenv(dotenv_path=env_path)

key = os.getenv("GEMINI_API_KEY")
print("Key found:", bool(key))
print("Value preview:", key[:10] + "..." if key else "None")
