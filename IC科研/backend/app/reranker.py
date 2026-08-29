from datetime import UTC, datetime

from .schemas import Evidence


def _recency(year: int | None) -> float:
    if not year:
        return 0.45
    age = max(0, datetime.now(UTC).year - year)
    return max(0.25, 1.0 - min(age, 20) / 25)


def score_evidence(
    evidence: Evidence, relevance: float, max_citations: int = 1
) -> Evidence:
    citation_influence = min(1.0, evidence.citation_count / max(max_citations, 1))
    score = (
        0.30 * relevance
        + 0.20 * evidence.authority_score
        + 0.15 * citation_influence
        + 0.15 * _recency(evidence.year)
        + 0.20 * evidence.engineering_applicability
    )
    return evidence.model_copy(update={"relevance": round(relevance, 4), "score": round(score, 4)})


def rerank(evidences: list[tuple[Evidence, float]]) -> list[Evidence]:
    max_citations = max((item.citation_count for item, _ in evidences), default=1)
    ranked = [score_evidence(item, relevance, max_citations) for item, relevance in evidences]
    return sorted(ranked, key=lambda item: item.score, reverse=True)

