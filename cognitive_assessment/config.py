from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Cognitive Assessment System"
    MAX_QUESTIONS_PER_SECTION: int = 5
    CONFIDENCE_THRESHOLD: float = 0.85
    MIN_QUESTIONS_BEFORE_STOP: int = 2
    SECTIONS: list = ["orientation", "memory", "reasoning"]
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = ""
    STM_WINDOW_SIZE: int = 6
    FAISS_TOP_K: int = 3
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"

settings = Settings()