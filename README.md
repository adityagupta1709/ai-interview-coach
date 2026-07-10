# AI Interview Coach

A multi-agent mock interview system with retrieval-augmented question selection,
persistent memory across sessions, and optional voice interaction. Built end-to-end
solo — architecture, agent design, retrieval pipeline, and frontend — on a zero-cost
stack.

**Author:** Aditya Gupta  · [GitHub](https://github.com/adityagupta1709))

---

## Why this exists

Most "AI agent" portfolio projects are a single prompt wearing a chatbot UI. This one
isn't: it's four agents with distinct responsibilities, coordinated by an orchestrator,
grounded by a retrieval layer instead of free-generating everything, and backed by
persistent memory so the system actually gets more useful the more you use it.

## Architecture

```
Resume + job description
          │
          ▼
   Resume/JD parser agent  ──►  detects role_type + target competencies
          │
          ▼
      Orchestrator  ◄──────────────────┐
     /     |      \                    │
    ▼      ▼       ▼                   │
Interviewer  Evaluator  Coach          │
 agent       agent      agent          │
    │         │           │            │
    └─────────┴───────────┘            │
              │                        │
              ▼                        │
       Session memory (SQLite) ────────┘
       tracks per-competency scores,
       feeds back into the orchestrator
       to target weak areas next time
```

Each agent is a separate, narrowly-scoped system prompt — not one prompt trying to
ask, score, and coach simultaneously. The orchestrator (plain Python, not an LLM)
owns the sequencing, so the control flow is deterministic and debuggable, while the
agents own the judgment calls within their own lane.

## RAG design

The interviewer doesn't invent questions from scratch — it retrieves them from a
tagged question bank and only uses the LLM to phrase the retrieved question naturally.

**Why retrieval instead of pure generation:** free-generated interview questions
drift generic over time and can't be tied back to a specific competency for scoring
or memory tracking. Retrieval keeps every question traceable to a `(role_type,
competency, difficulty)` tuple, which is what makes the memory/adaptivity loop
possible at all.

**Pipeline:**
1. `data/question_bank.json` holds curated questions, each tagged with `role_type`,
   `competency`, and `difficulty`
2. On first run, questions are embedded and indexed into **ChromaDB** using its
   bundled local embedding model (`all-MiniLM-L6-v2`, ONNX) — no external API call,
   no cost, fully offline after the one-time model download
3. At query time, `retrieve_question()` filters by `(role_type, competency)` first,
   then ranks candidates semantically within that filtered set — this hybrid
   approach avoids pure vector search surfacing a semantically-similar but
   practically-irrelevant question
4. Already-asked question IDs are excluded per session to avoid repeats
5. Retrieval falls back gracefully: exact tag match → role-only match → any unused
   question — so the system never dead-ends even with a small question bank

**Adaptive targeting:** before each new question, the orchestrator checks
`memory.get_weakest_competency(role_type)` — the competency with the lowest average
score across all past sessions for that role — and biases retrieval toward it. This
is what makes the system session-over-session adaptive rather than stateless.

## Agents

| Agent | Responsibility | Output |
|---|---|---|
| Resume/JD parser | Detects role type + top competencies to probe | Structured JSON |
| Interviewer | Naturally phrases the RAG-retrieved question | Text (+ optional audio) |
| Evaluator | Scores the answer on a fixed rubric | Structured JSON (forced schema) |
| Coach | Gives 2 actionable tips + a rewritten stronger answer | Text (+ optional audio) |

Forcing the evaluator into a fixed JSON schema (rather than free-text feedback) is
deliberate — it's what makes scores usable by code: averaged, tracked over time,
and fed back into the retrieval logic above.

## Voice layer

Optional, toggled per session. Speech-to-text via **Groq's free Whisper endpoint**,
text-to-speech via **edge-tts** (free, no key required). Both run through the same
orchestrator methods as the text flow — voice is an I/O layer on top of the same
agent pipeline, not a separate code path.

## Tech stack

- **LLM inference:** Groq (`llama-3.3-70b-versatile`), free tier
- **Retrieval:** ChromaDB with a local bundled embedding model
- **Persistent memory:** SQLite
- **Speech-to-text:** Groq Whisper
- **Text-to-speech:** edge-tts
- **Backend:** FastAPI
- **Frontend:** vanilla HTML/JS (chat-style interview flow + score history dashboard)

Every component runs on a free tier or fully local/open-source — total cost to run
this project is $0.

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   ```
   Mac/Linux: `source venv/bin/activate` · Windows: `venv\Scripts\activate`

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Get a free Groq API key at https://console.groq.com/keys (no card required).

4. Set up your `.env`:
   ```
   cp .env.example .env
   ```
   (Windows: `copy .env.example .env`) — then paste your key after `GROQ_API_KEY=`.

5. Run it:
   ```
   python main.py
   ```

6. Open **http://127.0.0.1:8000**

## Using it

1. Paste a job description and/or resume text (or leave blank), click **Analyze**
2. Set the number of questions, optionally enable **Use voice**
3. Click **Start interview** and answer each question — typed or spoken
4. Review scores and coaching feedback after each answer
5. At the end, view your history dashboard — scores persist across runs, and future
   sessions automatically target your weakest competency

## Roadmap / known limitations

- Sessions live in server memory (`SESSIONS` dict) — restarting the server ends any
  in-progress interview, though saved scores in `memory.sqlite3` persist
- The question bank is intentionally small (~20 questions) to start — designed to
  scale by appending more entries with the same schema, optionally sourced from
  public interview-question compilations
- Voice recording requires `localhost` or HTTPS (browser mic permission restriction)
- Single-user, no authentication — this is a personal practice tool, not a
  multi-tenant service
