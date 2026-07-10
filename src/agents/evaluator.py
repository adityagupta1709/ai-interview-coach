import json
from groq import Groq
from src.config import GROQ_API_KEY, MODEL

client = Groq(api_key=GROQ_API_KEY)

EVALUATOR_SYSTEM_PROMPT = """You are a strict interview evaluator. Given a question and an
answer, score the answer from 1-10 on each of these dimensions: structure, specificity,
technical_accuracy, communication.

Respond with ONLY valid JSON in exactly this schema, no other text, no markdown fences:
{"structure": <int>, "specificity": <int>, "technical_accuracy": <int>, "communication": <int>, "rationale": "<one sentence>"}
"""


class EvaluatorAgent:
    def score_answer(self, question: str, answer: str) -> dict:
        user_prompt = f"Question: {question}\n\nAnswer: {answer}"
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=300,
            messages=[
                {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw = response.choices[0].message.content.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {
                "structure": 5, "specificity": 5, "technical_accuracy": 5, "communication": 5,
                "rationale": "Could not parse evaluator output.", "raw": raw,
            }
