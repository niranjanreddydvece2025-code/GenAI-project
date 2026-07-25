import os
import pickle

import faiss
import numpy as np

from app.chatbot.gemini_client import embed_text
from app.core.config import settings

_EMBED_DIM = 3072  # gemini-embedding-001 output size

_meta_path = settings.faiss_index_path + ".meta.pkl"


class EmployeeIndex:
    """FAISS index over employee skill profiles, keyed by employee id."""

    def __init__(self):
        self.index = faiss.IndexFlatIP(_EMBED_DIM)
        self.employee_ids: list[int] = []

    def _profile_text(self, employee) -> str:
        parts = [
            f"Skills: {', '.join(employee.skills or [])}",
            f"Domain experience: {', '.join(employee.domain_experience or [])}",
            f"Certifications: {', '.join(employee.certifications or [])}",
            f"Experience: {employee.experience_years} years",
        ]
        return ". ".join(parts)

    def build(self, employees):
        self.index = faiss.IndexFlatIP(_EMBED_DIM)
        self.employee_ids = []
        vectors = []
        for emp in employees:
            vec = np.array(embed_text(self._profile_text(emp)), dtype="float32")
            vec = vec / (np.linalg.norm(vec) + 1e-10)
            vectors.append(vec)
            self.employee_ids.append(emp.id)
        if vectors:
            self.index.add(np.vstack(vectors))
        self._save()

    def add_employee(self, employee):
        vec = np.array(embed_text(self._profile_text(employee)), dtype="float32")
        vec = vec / (np.linalg.norm(vec) + 1e-10)
        self.index.add(np.expand_dims(vec, axis=0))
        self.employee_ids.append(employee.id)
        self._save()

    def search(self, query_text: str, top_k: int = 10) -> list[tuple[int, float]]:
        if self.index.ntotal == 0:
            return []
        vec = np.array(embed_text(query_text, task_type="RETRIEVAL_QUERY"), dtype="float32")
        vec = vec / (np.linalg.norm(vec) + 1e-10)
        scores, indices = self.index.search(np.expand_dims(vec, axis=0), min(top_k, self.index.ntotal))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self.employee_ids[idx], float(score)))
        return results

    def _save(self):
        os.makedirs(os.path.dirname(settings.faiss_index_path) or ".", exist_ok=True)
        faiss.write_index(self.index, settings.faiss_index_path)
        with open(_meta_path, "wb") as f:
            pickle.dump(self.employee_ids, f)

    def load(self) -> bool:
        if not os.path.exists(settings.faiss_index_path):
            return False
        self.index = faiss.read_index(settings.faiss_index_path)
        with open(_meta_path, "rb") as f:
            self.employee_ids = pickle.load(f)
        return True


employee_index = EmployeeIndex()
