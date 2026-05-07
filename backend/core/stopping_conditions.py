from config import settings
from core.context import SectionState


class StoppingConditions:

    @staticmethod
    def should_stop_section(section: SectionState) -> tuple[bool, str]:
        """Returns (should_stop, reason)"""

        # Hard stop: max questions reached
        if section.question_count >= settings.MAX_QUESTIONS_PER_SECTION:
            return True, "max_questions_reached"

        # Confidence stop: only after minimum questions
        if (
            section.question_count >= settings.MIN_QUESTIONS_BEFORE_STOP
            and section.confidence >= settings.CONFIDENCE_THRESHOLD
        ):
            return True, "confidence_threshold_met"

        return False, ""

    @staticmethod
    def should_stop_assessment(sections: dict, section_order: list) -> tuple[bool, str]:
        """Check if ALL sections are done."""
        all_done = all(sections[s].completed for s in section_order)
        if all_done:
            return True, "all_sections_complete"
        return False, ""