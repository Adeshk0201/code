from agents.base_agent import BaseAgent
from prompts.templates import build_consistency_prompt

class ConsistencyAgent(BaseAgent):
    async def analyze(self, patient_history: list, caretaker: dict) -> dict:
        system, user = build_consistency_prompt(patient_history, caretaker)
        result = await self._call(system, user, json_mode=True)
        return {
            "consistency_score": float(result.get("consistency_score", 1.0)),
            "mismatches": result.get("mismatches", []),
            "summary": result.get("summary", ""),
        }