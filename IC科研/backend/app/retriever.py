import math
import re
from collections import Counter

from .reranker import rerank
from .schemas import Evidence, QuestionCategory
from .seed_data import EVIDENCE_CATALOG


def _tokens(text: str) -> list[str]:
    english = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", text.lower())
    chinese = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    return english + chinese


class HybridRetriever:
    """MVP hybrid retrieval: BM25-like lexical score + semantic token overlap + domain priors.

    PostgreSQL/pgvector storage is represented by the models and migration. The in-process
    catalog keeps development mode runnable before a database is provisioned.
    """

    def __init__(self, catalog: list[Evidence] | None = None):
        self.catalog = catalog or EVIDENCE_CATALOG
        self.documents = [
            _tokens(" ".join([e.title, e.excerpt, " ".join(e.domains)])) for e in self.catalog
        ]
        self.avg_length = sum(map(len, self.documents)) / max(len(self.documents), 1)

    def _bm25(self, query: list[str], index: int) -> float:
        document = self.documents[index]
        frequencies = Counter(document)
        score = 0.0
        k1, b = 1.5, 0.75
        for term in query:
            document_frequency = sum(term in candidate for candidate in self.documents)
            if not document_frequency:
                continue
            inverse_frequency = math.log(
                1 + (len(self.documents) - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            term_frequency = frequencies[term]
            denominator = term_frequency + k1 * (
                1 - b + b * len(document) / max(self.avg_length, 1)
            )
            score += inverse_frequency * (term_frequency * (k1 + 1)) / max(denominator, 1e-9)
        return score

    def retrieve(
        self,
        query_expansions: list[str],
        category: QuestionCategory,
        limit: int = 6,
    ) -> list[Evidence]:
        query_tokens = _tokens(" ".join(query_expansions))
        query_set = set(query_tokens)
        candidates: list[tuple[Evidence, float]] = []
        bm25_scores = [self._bm25(query_tokens, i) for i in range(len(self.catalog))]
        bm25_max = max(bm25_scores, default=1) or 1

        for index, evidence in enumerate(self.catalog):
            document_set = set(self.documents[index])
            semantic = len(query_set & document_set) / max(len(query_set), 1)
            lexical = bm25_scores[index] / bm25_max
            domain = 1.0 if category.value in evidence.domains else 0.15
            relevance = min(1.0, 0.48 * lexical + 0.32 * semantic + 0.20 * domain)
            if relevance >= 0.12:
                candidates.append((evidence, relevance))
        return rerank(candidates)[:limit]

