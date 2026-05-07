from app.config import SECTIONS

class SectionManager:
    def __init__(self):
        self.sections = SECTIONS
        self.index = 0

    def current(self):
        return self.sections[self.index]

    def next(self):
        self.index += 1

        if self.index >= len(self.sections):
            return None

        return self.sections[self.index]