from .retriever import HybridRetriever
from .schemas import Evidence, QuestionCategory


class IndustryRetriever:
    def __init__(self) -> None:
        self.hybrid = HybridRetriever()

    def search(
        self, query_expansions: list[str], category: QuestionCategory, limit: int = 6
    ) -> list[Evidence]:
        return self.hybrid.retrieve(query_expansions, category, limit)

