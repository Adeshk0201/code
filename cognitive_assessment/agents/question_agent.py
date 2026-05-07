from agents.base_agent import BaseAgent
from prompts.templates import build_question_prompt
from config import settings

class QuestionAgent(BaseAgent):
    async def generate(self, ctx_snapshot: dict) -> str:
        system, user = build_question_prompt(
            ctx_snapshot,
            max_q=settings.MAX_QUESTIONS_PER_SECTION,
            conf_threshold=settings.CONFIDENCE_THRESHOLD,
        )
        question = await self._call(system, user, json_mode=False)
        return question.strip()