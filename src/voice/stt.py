from groq import Groq
from src.config import GROQ_API_KEY, WHISPER_MODEL

client = Groq(api_key=GROQ_API_KEY)


def transcribe(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=f,
            model=WHISPER_MODEL,
        )
    return result.text.strip()
