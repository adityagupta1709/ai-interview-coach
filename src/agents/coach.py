from groq import Groq
from src.config import GROQ_API_KEY, MODEL

client = Groq(api_key=GROQ_API_KEY)

COACH_SYSTEM_PROMPT = """You are a supportive but honest interview coach. Given a question,
the candidate's answer, and rubric scores, provide:
1. Two specific, actionable improvement tips (not generic advice).
2. A rewritten, stronger version of the answer, using the STAR method where relevant.
Keep the tone encouraging but direct. Be concise - under 150 words total.
"""


class CoachAgent:
    def give_feedback(self, question: str, answer: str, scores: dict) -> str:
        user_prompt = (
            f"Question: {question}\n\nCandidate answer: {answer}\n\nScores: {scores}"
        )
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=400,
            messages=[
                {"role": "system", "content": COACH_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()
