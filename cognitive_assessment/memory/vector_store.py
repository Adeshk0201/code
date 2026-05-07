import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """FAISS-based semantic memory store."""

    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dim = 384  # all-MiniLM-L6-v2 output dim
        self.index = faiss.IndexFlatL2(self.dim)
        self.documents: list[dict] = []  # parallel list to FAISS index

    def _embed(self, text: str) -> np.ndarray:
        vec = self.model.encode([text], convert_to_numpy=True)
        return vec.astype("float32")

    def add(self, text: str, metadata: dict):
        vec = self._embed(text)
        self.index.add(vec)
        self.documents.append({"text": text, "meta": metadata})
        logger.info(f"VectorStore: added doc #{len(self.documents)}")

    def search(self, query: str, top_k: int = None) -> list[dict]:
        k = top_k or settings.FAISS_TOP_K
        if self.index.ntotal == 0:
            return []
        vec = self._embed(query)
        distances, indices = self.index.search(vec, min(k, self.index.ntotal))
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0:
                results.append({
                    "text": self.documents[idx]["text"],
                    "meta": self.documents[idx]["meta"],
                    "distance": float(dist),
                })
        return results

    def add_interaction(self, section: str, question: str, answer: str, session_id: str):
        text = f"Section: {section}\nQ: {question}\nA: {answer}"
        self.add(text, {"section": section, "session_id": session_id, "type": "interaction"})

    def add_summary(self, summary: str, session_id: str):
        self.add(summary, {"session_id": session_id, "type": "summary"})

    def retrieve_relevant(self, query: str) -> str:
        results = self.search(query)
        if not results:
            return "No relevant memory found."
        return "\n---\n".join(r["text"] for r in results)