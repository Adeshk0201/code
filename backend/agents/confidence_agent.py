from agents.base_agent import BaseAgent
from prompts.templates import build_confidence_prompt

class ConfidenceAgent(BaseAgent):
    async def evaluate(self, ctx_snapshot: dict, answer: str) -> dict:
        system, user = build_confidence_prompt(ctx_snapshot, answer)
        result = await self._call(system, user, json_mode=True)
        return {
            "confidence": float(result.get("confidence", 0.5)),
            "reason": result.get("reason", ""),
        }