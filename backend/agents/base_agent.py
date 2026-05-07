from llm.base_llm import BaseLLM
import json

class BaseAgent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def _call(self, system: str, user: str, json_mode: bool = True) -> dict | str:
        raw = await self.llm.complete(system, user, json_mode=json_mode)
        if json_mode:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"error": "parse_failed", "raw": raw}
        return raw