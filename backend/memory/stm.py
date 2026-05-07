from collections import deque
from config import settings


class ShortTermMemory:
    """Sliding window of recent interactions for immediate context coherence."""

    def __init__(self):
        self._window = deque(maxlen=settings.STM_WINDOW_SIZE)

    def add(self, section: str, question: str, answer: str, score: float, confidence: float):
        self._window.append({
            "section": section,
            "q": question,
            "a": answer,
            "score": score,
            "confidence": confidence,
        })

    def get_recent(self, n: int = None) -> list:
        items = list(self._window)
        return items[-n:] if n else items

    def format_for_prompt(self) -> str:
        if not self._window:
            return "No recent interactions."
        return "\n".join(
            f"[{i['section']}] Q: {i['q']}\nA: {i['a']} (score={i['score']:.2f})"
            for i in self._window
        )

    def clear(self):
        self._window.clear()