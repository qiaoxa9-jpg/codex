from .schemas import ConceptSummary
from .seed_data import CONCEPTS


class ConceptRetriever:
    def search(self, query: str = "", category: str | None = None) -> list[ConceptSummary]:
        normalized = query.lower().strip()
        return [
            concept
            for concept in CONCEPTS
            if (not category or concept.category == category)
            and (
                not normalized
                or normalized in concept.name.lower()
                or normalized in concept.chinese_name.lower()
                or normalized in (concept.abbreviation or "").lower()
                or normalized in concept.definition.lower()
            )
        ]

    def get(self, concept_id: str) -> ConceptSummary | None:
        return next((concept for concept in CONCEPTS if concept.id == concept_id), None)

