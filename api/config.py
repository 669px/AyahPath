import os
from dotenv import load_dotenv

# Search for .env in current directory and parent directory
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('../.env'):
    load_dotenv('../.env')

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "google/gemini-2.0-flash-001")
    DATA_DIR = os.getenv("DATA_DIR", "data")
    PORT = int(os.getenv("API_PORT", 5001))
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
