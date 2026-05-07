from config import settings
from core.context import Context


class SectionManager:

    def __init__(self):
        self.section_order = settings.SECTIONS

    def get_next_section(self, ctx: Context) -> str | None:
        current_idx = self.section_order.index(ctx.current_section)
        next_idx = current_idx + 1
        if next_idx < len(self.section_order):
            return self.section_order[next_idx]
        return None

    def transition_section(self, ctx: Context, reason: str) -> bool:
        """Mark current section complete. Move to next. Returns False if assessment done."""
        ctx.active_section.completed = True
        next_sec = self.get_next_section(ctx)
        if next_sec:
            ctx.current_section = next_sec
            return True  # moved to next
        else:
            ctx.assessment_complete = True
            ctx.stop_reason = reason
            return False  # assessment done

    def get_section_prompt_hint(self, section_name: str) -> str:
        hints = {
            "orientation": "Ask about time, date, place, and person orientation.",
            "memory": "Test short-term and long-term memory recall.",
            "reasoning": "Test logical thinking, problem solving, and abstract reasoning.",
        }
        return hints.get(section_name, "")