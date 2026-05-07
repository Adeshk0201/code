from agents.question_agent import QuestionAgent
from agents.confidence_agent import ConfidenceAgent
from agents.scoring_agent import ScoringAgent
from agents.consistency_agent import ConsistencyAgent
from agents.summarizer_agent import SummarizerAgent
from llm.openai_provider import get_llm

class AgentOrchestrator:
    def __init__(self):
        llm = get_llm()
        self.question_agent = QuestionAgent(llm)
        self.confidence_agent = ConfidenceAgent(llm)
        self.scoring_agent = ScoringAgent(llm)
        self.consistency_agent = ConsistencyAgent(llm)
        self.summarizer_agent = SummarizerAgent(llm)

    async def get_question(self, ctx_snapshot: dict) -> str:
        return await self.question_agent.generate(ctx_snapshot)

    async def get_confidence(self, ctx_snapshot: dict, answer: str) -> dict:
        return await self.confidence_agent.evaluate(ctx_snapshot, answer)

    async def score_section(self, section: str, history: list, caretaker: dict) -> dict:
        return await self.scoring_agent.score_section(section, history, caretaker)

    async def check_consistency(self, patient_history: list, caretaker: dict) -> dict:
        return await self.consistency_agent.analyze(patient_history, caretaker)

    async def generate_report(self, scores: dict, consistency: dict, patient: dict) -> dict:
        return await self.summarizer_agent.generate_report(scores, consistency, patient)