import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
import edge_tts
from src.config import AUDIO_DIR, TTS_VOICE

# Runs asyncio.run() in a plain OS thread with no event loop of its own,
# so it never collides with the event loop FastAPI/uvicorn is already running.
_executor = ThreadPoolExecutor(max_workers=2)


async def _synthesize(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    await communicate.save(out_path)


def synthesize_to_file(text: str) -> str:
    """Generates an mp3 for the given text and returns its filename
    (relative to the static/audio directory)."""
    filename = f"{uuid.uuid4().hex}.mp3"
    out_path = str(AUDIO_DIR / filename)
    future = _executor.submit(asyncio.run, _synthesize(text, out_path))
    future.result()
    return filename

