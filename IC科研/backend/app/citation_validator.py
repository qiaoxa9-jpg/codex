from .schemas import AnswerSection, Citation, Evidence


class CitationValidationError(ValueError):
    pass


def validate_and_build_citations(
    sections: list[AnswerSection], evidences: list[Evidence]
) -> list[Citation]:
    evidence_by_id = {evidence.source_id: evidence for evidence in evidences}
    used: list[str] = []
    for section in sections:
        for source_id in section.source_ids:
            if source_id not in evidence_by_id:
                raise CitationValidationError(
                    f"Generated source_id is absent from Evidence Context: {source_id}"
                )
            if source_id not in used:
                used.append(source_id)
    return [
        Citation(
            number=index,
            source_id=source_id,
            title=evidence_by_id[source_id].title,
            url=evidence_by_id[source_id].url,
        )
        for index, source_id in enumerate(used, start=1)
    ]

