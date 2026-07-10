import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.orchestrator import InterviewSession
from src.agents.resume_parser import ResumeParserAgent
from src.memory import db as memory
from src.voice.stt import transcribe

app = FastAPI(title="AI Interview Coach")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

memory.init_db()
SESSIONS: dict[str, InterviewSession] = {}
parser = ResumeParserAgent()


@app.get("/")
def root():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.post("/api/parse-profile")
def parse_profile(resume_text: str = Form(""), job_description: str = Form("")):
    if not resume_text and not job_description:
        return {"role_type": "General", "competencies": ["communication", "ambiguity"]}
    return parser.parse(resume_text, job_description)


@app.post("/api/session/start")
def start_session(
    role_type: str = Form(...),
    competencies: str = Form(""),  # comma-separated
    num_questions: int = Form(5),
    voice: bool = Form(False),
):
    comp_list = [c.strip() for c in competencies.split(",") if c.strip()]
    session = InterviewSession(role_type, comp_list, num_questions, voice)
    SESSIONS[session.session_id] = session
    first_question = session.next_question()
    return {"session_id": session.session_id, **first_question}


@app.post("/api/session/{session_id}/answer")
async def submit_answer(
    session_id: str,
    answer_text: str = Form(""),
    audio: UploadFile = File(None),
):
    session = SESSIONS[session_id]

    final_answer_text = answer_text
    if audio is not None:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name
        final_answer_text = transcribe(tmp_path)

    feedback_result = session.submit_answer(final_answer_text)
    next_q = session.next_question()

    return {
        "transcript": final_answer_text,
        **feedback_result,
        "next": next_q,
    }


@app.get("/api/history")
def history():
    return memory.get_history()


@app.get("/api/audio/{filename}")
def get_audio(filename: str):
    audio_path = STATIC_DIR / "audio" / filename
    return FileResponse(str(audio_path), media_type="audio/mpeg")
