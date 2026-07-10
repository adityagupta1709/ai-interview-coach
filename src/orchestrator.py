import uuid
from src.agents.interviewer import InterviewerAgent
from src.agents.evaluator import EvaluatorAgent
from src.agents.coach import CoachAgent
from src.rag.question_store import retrieve_question
from src.memory import db as memory
from src.voice.tts import synthesize_to_file


class InterviewSession:
    def __init__(self, role_type: str, competencies: list[str], num_questions: int, voice: bool):
        self.session_id = uuid.uuid4().hex
        self.role_type = role_type
        self.competencies = competencies or ["communication", "ambiguity"]
        self.num_questions = num_questions
        self.voice = voice

        self.interviewer = InterviewerAgent(role_type)
        self.evaluator = EvaluatorAgent()
        self.coach = CoachAgent()

        self.asked_ids: list[str] = []
        self.question_count = 0
        self.done = False
        self.current_question = None  # dict: id, text (seed), competency, phrased

    def _pick_competency(self) -> str:
        # Prefer the weakest competency from past sessions for this role, if we have history.
        weakest = memory.get_weakest_competency(self.role_type)
        if weakest and weakest in self.competencies:
            return weakest
        return self.competencies[self.question_count % len(self.competencies)]

    def next_question(self) -> dict:
        if self.question_count >= self.num_questions:
            self.done = True
            return {"done": True}

        competency = self._pick_competency()
        seed = retrieve_question(self.role_type, competency, self.asked_ids)
        if seed is None:
            seed = {"id": "fallback", "text": f"Tell me about a challenge related to {competency}.",
                    "competency": competency}

        self.asked_ids.append(seed["id"])
        phrased = self.interviewer.phrase_question(seed["text"])
        self.current_question = {
            "id": seed["id"],
            "seed_text": seed["text"],
            "competency": seed.get("competency", competency),
            "text": phrased,
        }
        self.question_count += 1

        result = {
            "done": False,
            "question_number": self.question_count,
            "total_questions": self.num_questions,
            "question": phrased,
        }
        if self.voice:
            result["question_audio"] = synthesize_to_file(phrased)
        return result

    def submit_answer(self, answer_text: str) -> dict:
        q = self.current_question
        scores = self.evaluator.score_answer(q["text"], answer_text)
        feedback = self.coach.give_feedback(q["text"], answer_text, scores)

        memory.save_answer(
            session_id=self.session_id,
            role_type=self.role_type,
            question_id=q["id"],
            competency=q["competency"],
            question=q["text"],
            answer=answer_text,
            scores=scores,
        )

        result = {
            "scores": scores,
            "feedback": feedback,
            "is_last": self.question_count >= self.num_questions,
        }
        if self.voice:
            result["feedback_audio"] = synthesize_to_file(feedback)
        return result
