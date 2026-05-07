from app.core.context import Context
from app.core.section_manager import SectionManager
from app.core.stop_conditions import should_stop

class Controller:

    def __init__(self):
        self.context = Context()
        self.section_manager = SectionManager()

    async def generate_question(self):

        section = self.context.state.current_section

        return f"{section} Question {self.context.state.question_count + 1}"

    async def evaluate_confidence(self):

        q = self.context.state.question_count

        return min(0.2 * q, 1.0)

    async def process_answer(self, question, answer):

        self.context.update_history(question, answer)

        self.context.increment_questions()

        confidence = await self.evaluate_confidence()

        self.context.update_confidence(confidence)

    async def run(self, answer=None):

        if should_stop(self.context):

            nxt = self.section_manager.next()

            if nxt is None:
                self.context.stop_assessment()
                return {"status": "completed"}

            self.context.set_section(nxt)

            self.context.state.question_count = 0
            self.context.state.confidence = 0

        question = await self.generate_question()

        return {
            "section": self.context.state.current_section,
            "question": question,
            "confidence": self.context.state.confidence
        }