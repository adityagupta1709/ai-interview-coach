import sqlite3
from datetime import datetime
from src.config import DB_PATH


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role_type TEXT NOT NULL,
            question_id TEXT,
            competency TEXT,
            question TEXT,
            answer TEXT,
            structure INTEGER,
            specificity INTEGER,
            technical_accuracy INTEGER,
            communication INTEGER,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_answer(session_id, role_type, question_id, competency, question, answer, scores):
    conn = _connect()
    conn.execute(
        """
        INSERT INTO answers
        (session_id, role_type, question_id, competency, question, answer,
         structure, specificity, technical_accuracy, communication, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            role_type,
            question_id,
            competency,
            question,
            answer,
            scores.get("structure"),
            scores.get("specificity"),
            scores.get("technical_accuracy"),
            scores.get("communication"),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_weakest_competency(role_type: str) -> str | None:
    """Returns the competency with the lowest average overall score for this
    role, so the next session can target it. None if there's no history yet."""
    conn = _connect()
    rows = conn.execute(
        """
        SELECT competency,
               AVG((structure + specificity + technical_accuracy + communication) / 4.0) AS avg_score
        FROM answers
        WHERE role_type = ? AND competency IS NOT NULL
        GROUP BY competency
        ORDER BY avg_score ASC
        LIMIT 1
        """,
        (role_type,),
    ).fetchone()
    conn.close()
    return rows["competency"] if rows else None


def get_history(limit: int = 20) -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        """
        SELECT session_id, role_type, competency, question,
               structure, specificity, technical_accuracy, communication, created_at
        FROM answers
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
