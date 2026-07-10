from groq import Groq
from src.config import GROQ_API_KEY, MODEL

client = Groq(api_key=GROQ_API_KEY)

INTERVIEWER_SYSTEM_PROMPT = """You are an experienced interviewer conducting a mock interview.
You will be given a seed question pulled from a question bank. Rephrase it naturally in your
own voice, the way a real interviewer would ask it out loud - conversational, not robotic.
Do not change the underlying intent of the question. Do not add preamble like "Great, here's
a question" - just ask it directly, in one or two sentences.
"""


class InterviewerAgent:
    def __init__(self, role_type: str):
        self.role_type = role_type
        self.system_prompt = (
            f"{INTERVIEWER_SYSTEM_PROMPT}\nThe candidate is interviewing for a "
            f"{role_type} role."
        )

    def phrase_question(self, seed_question: str) -> str:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=200,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Seed question: {seed_question}"},
            ],
        )
        return response.choices[0].message.content.strip()
