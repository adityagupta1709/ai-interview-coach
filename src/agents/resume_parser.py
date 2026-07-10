import json
from groq import Groq
from src.config import GROQ_API_KEY, MODEL

client = Groq(api_key=GROQ_API_KEY)

PARSER_SYSTEM_PROMPT = """You extract structured interview-prep signal from a candidate's
resume and/or a job description. Identify:
- role_type: pick the single closest match from ["TPM", "Software Engineer", "AI Engineer", "General"]
- competencies: the 3-4 most important competencies to test for this role, chosen from
  ["leadership", "stakeholder_management", "prioritization", "failure", "product_sense",
   "system_design", "technical_depth", "conflict_resolution", "ambiguity", "communication"]

Respond with ONLY valid JSON, no other text, no markdown fences:
{"role_type": "<one of the options above>", "competencies": ["<3-4 items from the list above>"]}
"""


class ResumeParserAgent:
    def parse(self, resume_text: str, job_description: str) -> dict:
        user_prompt = f"Resume:\n{resume_text}\n\nJob description:\n{job_description}"
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=200,
            messages=[
                {"role": "system", "content": PARSER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw = response.choices[0].message.content.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"role_type": "General", "competencies": ["communication", "ambiguity"]}
