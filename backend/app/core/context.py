from app.schemas.models import ContextModel

class Context:
    def __init__(self):
        self.state = ContextModel()

    def update_history(self, q, a):
        self.state.history.append({
            "question": q,
            "answer": a
        })

    def update_confidence(self, value):
        self.state.confidence = value

    def increment_questions(self):
        self.state.question_count += 1

    def set_section(self, section):
        self.state.current_section = section

    def stop_assessment(self):
        self.state.stop = True