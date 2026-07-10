import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("INTERVIEW_COACH_MODEL", "llama-3.3-70b-versatile")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo")
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-GuyNeural")

QUESTION_BANK_PATH = BASE_DIR / "data" / "question_bank.json"
CHROMA_DIR = str(BASE_DIR / "chroma_db")
DB_PATH = str(BASE_DIR / "memory.sqlite3")
AUDIO_DIR = BASE_DIR / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY not found. Copy .env.example to .env and add your free key "
        "from https://console.groq.com/keys"
    )
