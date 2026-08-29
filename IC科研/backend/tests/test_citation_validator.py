import pytest

from app.citation_validator import CitationValidationError, validate_and_build_citations
from app.schemas import AnswerSection
from app.seed_data import EVIDENCE_CATALOG


def test_builds_stable_numbered_citations() -> None:
    source_id = EVIDENCE_CATALOG[0].source_id
    citations = validate_and_build_citations(
        [AnswerSection(key="solution", title="Solution", content="text", source_ids=[source_id])],
        EVIDENCE_CATALOG,
    )
    assert citations[0].number == 1
    assert citations[0].source_id == source_id


def test_rejects_source_id_outside_evidence_context() -> None:
    sections = [
        AnswerSection(
            key="bad",
            title="Bad",
            content="hallucinated",
            source_ids=["PAPER-DOES-NOT-EXIST"],
        )
    ]
    with pytest.raises(CitationValidationError):
        validate_and_build_citations(sections, EVIDENCE_CATALOG)

