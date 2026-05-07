from agents.base_agent import BaseAgent
from prompts.templates import build_scoring_prompt

class ScoringAgent(BaseAgent):
    async def score_section(self, section: str, history: list, caretaker: dict) -> dict:
        system, user = build_scoring_prompt(section, history, caretaker)
        result = await self._call(system, user, json_mode=True)
        return {
            "section_score": float(result.get("section_score", 0.0)),
            "observations": result.get("observations", ""),
        }