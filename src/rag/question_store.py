import json
import chromadb
from src.config import QUESTION_BANK_PATH, CHROMA_DIR

_client = chromadb.PersistentClient(path=CHROMA_DIR)
_collection = _client.get_or_create_collection(name="questions")


def index_question_bank():
    """Load question_bank.json into Chroma if it isn't indexed yet.
    Uses Chroma's bundled local embedding model - no external API, no cost."""
    if _collection.count() > 0:
        return

    with open(QUESTION_BANK_PATH) as f:
        questions = json.load(f)

    _collection.add(
        ids=[q["id"] for q in questions],
        documents=[q["text"] for q in questions],
        metadatas=[
            {
                "role_type": q["role_type"],
                "competency": q["competency"],
                "difficulty": q["difficulty"],
            }
            for q in questions
        ],
    )


def retrieve_question(role_type: str, competency: str, exclude_ids: list[str]) -> dict | None:
    """Retrieve the best-matching unused question for this role + competency.
    Falls back to role-only, then to any unused question, if nothing matches."""
    index_question_bank()

    for where in (
        {"$and": [{"role_type": role_type}, {"competency": competency}]},
        {"role_type": role_type},
        {},
    ):
        results = _collection.query(
            query_texts=[f"{competency} interview question for {role_type}"],
            n_results=10,
            where=where if where else None,
        )
        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        for qid, doc, meta in zip(ids, docs, metas):
            if qid not in exclude_ids:
                return {"id": qid, "text": doc, **meta}

    return None
