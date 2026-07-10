# AI Interview Coach — full package

A multi-agent, voice-enabled mock interview system with RAG-driven questions and
persistent memory across sessions. Runs entirely on free tools.

## What's inside

- **RAG question bank** — curated, tagged questions (`data/question_bank.json`)
  retrieved via ChromaDB (local embeddings, no API cost) filtered by role and
  competency
- **Resume/JD parser agent** — paste a resume and/or job description, it detects
  the role type and the competencies worth probing
- **Interviewer agent** — phrases the retrieved question naturally
- **Evaluator agent** — scores each answer on a fixed rubric (structured JSON)
- **Coach agent** — gives two actionable tips + a rewritten stronger answer
- **Persistent memory** — SQLite store; each new session targets whichever
  competency you've historically scored lowest on
- **Voice** — optional. Groq Whisper (free) for speech-to-text, `edge-tts` (free)
  for text-to-speech
- **Frontend** — a real browser UI: paste your profile, answer by typing or by
  recording your voice, see live scores and feedback, and a history dashboard

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   ```
   Mac/Linux: `source venv/bin/activate`
   Windows: `venv\Scripts\activate`

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Get a free Groq API key at https://console.groq.com/keys (no card required).

4. Set up your `.env`:
   ```
   cp .env.example .env
   ```
   (Windows: `copy .env.example .env`)
   Open `.env` and paste your key after `GROQ_API_KEY=`.

5. Run it:
   ```
   python main.py
   ```

6. Open your browser to **http://127.0.0.1:8000**

## Using it

1. Paste a job description and/or resume text (or leave blank), click **Analyze**
   — it detects the role type and key competencies
2. Set how many questions you want, optionally check **Use voice**
3. Click **Start interview**
4. Answer each question (typed, or recorded if voice is on — your browser will
   ask for microphone permission the first time)
5. See your scores and coaching feedback after each answer
6. At the end, see your history dashboard — scores are saved permanently in
   `memory.sqlite3`, so future sessions automatically target your weakest areas

## Notes on the free stack

- **LLM**: Groq's `llama-3.3-70b-versatile`, free tier
- **Embeddings for RAG**: ChromaDB's bundled local model — runs on your machine,
  no API call, no cost
- **Speech-to-text**: Groq Whisper, same free account as the LLM
- **Text-to-speech**: `edge-tts`, free, no key needed
- **Storage**: SQLite (`memory.sqlite3`) and ChromaDB (`chroma_db/`), both local
  files created automatically on first run

## Known limitations (worth knowing, and worth mentioning if asked in an interview)

- Sessions live in server memory (`SESSIONS` dict in `src/api.py`) — restarting
  the server loses any interview in progress, though saved scores in
  `memory.sqlite3` persist
- The question bank is small (~20 questions) — easy to expand by adding more
  entries to `data/question_bank.json` with the same schema
- Voice recording uses the browser's `MediaRecorder` API, which needs Chrome,
  Edge, or Firefox over `http://localhost` (works fine locally; would need HTTPS
  if ever deployed to a real domain)
- No authentication — this is a single-user local app, not multi-tenant
