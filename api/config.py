import os
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for candidate in (os.path.join(BASE_DIR, '.env'), os.path.join(os.path.dirname(BASE_DIR), '.env')):
    if os.path.exists(candidate):
        load_dotenv(candidate)
        break

def _resolve_data_dir():
    data_dir = os.getenv('DATA_DIR', 'data')
    if os.path.isabs(data_dir):
        return data_dir
    return os.path.join(BASE_DIR, data_dir)

def _env_float(name, default):
    value = os.getenv(name, str(default))
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)

def _env_int(name, default):
    value = os.getenv(name, str(default))
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)

class Config:
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    AI_MODEL = os.getenv('AI_MODEL', 'mistralai/mistral-7b-instruct')
    QURAN_CLIENT_ID = os.getenv('QURAN_CLIENT_ID', '')
    QURAN_CLIENT_SECRET = os.getenv('QURAN_CLIENT_SECRET', '')
    QURAN_AUTH_BASE_URL = os.getenv('QURAN_AUTH_BASE_URL', 'https://oauth2.quran.foundation')
    QURAN_API_BASE_URL = os.getenv('QURAN_API_BASE_URL', 'https://apis.quran.foundation')
    QURAN_MCP_BASE_URL = os.getenv('QURAN_MCP_BASE_URL', '')
    QURAN_MCP_TIMEOUT_SECONDS = _env_float('QURAN_MCP_TIMEOUT_SECONDS', 6)
    QURAN_API_TIMEOUT_SECONDS = _env_float('QURAN_API_TIMEOUT_SECONDS', 12)
    QURAN_MCP_FAIL_COOLDOWN_SECONDS = _env_int('QURAN_MCP_FAIL_COOLDOWN_SECONDS', 300)
    QURAN_USE_OFFICIAL_API = os.getenv('QURAN_USE_OFFICIAL_API', 'auto').lower()
    QURAN_DEFAULT_TRANSLATION = os.getenv('QURAN_DEFAULT_TRANSLATION', '131')
    QURAN_DEFAULT_RECITATION = os.getenv('QURAN_DEFAULT_RECITATION', '7')
    QURAN_DEFAULT_TAFSIR = os.getenv('QURAN_DEFAULT_TAFSIR', '169')
    DATA_DIR = _resolve_data_dir()
    PORT = int(os.getenv('API_PORT', 5001))
    DEBUG = os.getenv('API_DEBUG', '').lower() in {'1', 'true', 'yes'}
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv('AYAHPATH_ALLOWED_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',') if origin.strip()]
    HADITH_API_KEY = os.getenv('HADITH_API_KEY', '$2y$10$nbYnPpXkToWTEsxVuG3VHAt8ZXHsWYnajvI7sUIGMkSF3MfHpDYS')
