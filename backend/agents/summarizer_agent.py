from agents.base_agent import BaseAgent
from prompts.templates import build_summarizer_prompt

class SummarizerAgent(BaseAgent):
    async def generate_report(self, scores: dict, consistency: dict, patient: dict) -> dict:
        system, user = build_summarizer_prompt(scores, consistency, patient)
        result = await self._call(system, user, json_mode=True)
        return {
            "report": result.get("report", ""),
            "risk_level": result.get("risk_level", "unknown"),
            "recommendations": result.get("recommendations", []),
        }