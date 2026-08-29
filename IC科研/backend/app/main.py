import re

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .answer_generator import AnswerGenerator
from .citation_validator import validate_and_build_citations
from .concept_retriever import ConceptRetriever
from .config import get_settings
from .engineering_agent import EngineeringAgent
from .industry_retriever import IndustryRetriever
from .paper_retriever import PaperRetriever
from .query_analyzer import QueryAnalyzer
from .research_agent import ResearchAgent
from .reranker import rerank
from .schemas import (
    AnswerMode,
    ConceptSummary,
    Evidence,
    EvidenceLevel,
    PaperResult,
    PaperSearchResponse,
    ResearchRequest,
    ResearchResponse,
    RetrievalTrace,
)

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Evidence-grounded semiconductor research and Digital IC engineering API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = QueryAnalyzer()
industry_retriever = IndustryRetriever()
paper_retriever = PaperRetriever(settings)
concept_retriever = ConceptRetriever()
generator = AnswerGenerator(settings)
engineering_agent = EngineeringAgent(generator)
research_agent = ResearchAgent(generator)


def papers_as_evidence(papers: list[PaperResult], domain: str) -> list[Evidence]:
    candidates: list[tuple[Evidence, float]] = []
    for index, paper in enumerate(papers):
        if not paper.abstract:
            continue
        excerpt = re.sub(r"<[^>]+>", " ", paper.abstract)
        excerpt = re.sub(r"\s+", " ", excerpt).strip()[:1200]
        provider = "S2" if paper.source == "Semantic Scholar" else "CROSSREF"
        candidates.append(
            (
                Evidence(
                    source_id=f"PAPER-{provider}-{paper.paper_id}"[:220],
                    title=paper.title,
                    source=paper.source,
                    document_type="Research Paper",
                    url=paper.url,
                    year=paper.year,
                    authors=paper.authors,
                    venue=paper.venue,
                    doi=paper.doi,
                    citation_count=paper.citation_count,
                    open_access=paper.open_access,
                    excerpt=excerpt,
                    domains=[domain],
                    authority_score=0.78,
                    engineering_applicability=0.55,
                    evidence_level=EvidenceLevel.RESEARCH_SUPPORTED,
                    metadata={"paper_id": paper.paper_id, "provider": paper.source},
                ),
                max(0.45, 0.82 - index * 0.05),
            )
        )
    return rerank(candidates)


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": settings.app_name, "docs": "/docs", "health": f"{settings.api_prefix}/health"}


@app.get(f"{settings.api_prefix}/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": "seeded-development", "version": "0.1.0"}


@app.post(f"{settings.api_prefix}/research/ask", response_model=ResearchResponse)
async def ask(request: ResearchRequest) -> ResearchResponse:
    classification = analyzer.analyze(request.question)
    expansions = analyzer.expand(request.question, classification.category)
    related_concepts = concept_retriever.search(category=classification.category.value)
    if related_concepts:
        expansions.append(
            " ".join(
                filter(
                    None,
                    [
                        term
                        for concept in related_concepts[:8]
                        for term in (concept.name, concept.abbreviation, concept.chinese_name)
                    ],
                )
            )
        )
    evidences = industry_retriever.search(
        expansions, classification.category, request.max_evidence
    )
    external_status = {"semantic_scholar": "skipped", "crossref": "skipped"}
    channels = ["BM25", "semantic-overlap", "industry-documents", "concept-prior"]
    paper_candidates = 0

    if request.mode == AnswerMode.RESEARCH:
        papers, external_status = await paper_retriever.search(request.question, limit=8)
        paper_evidence = papers_as_evidence(papers, classification.category.value)
        paper_candidates = len(paper_evidence)
        evidences = sorted(
            [*evidences, *paper_evidence], key=lambda item: item.score, reverse=True
        )[: request.max_evidence]
        channels.append("paper-metadata")

    if request.mode == AnswerMode.RESEARCH:
        sections, status, warnings = await research_agent.run(
            request.question, classification, evidences, request.language
        )
    elif request.mode == AnswerMode.ENGINEERING:
        sections, status, warnings = await engineering_agent.run(
            request.question, classification, evidences, request.language
        )
    else:
        sections, status, warnings = await generator.generate(
            request.question, request.mode, classification, evidences, request.language
        )
    citations = validate_and_build_citations(sections, evidences)
    return ResearchResponse(
        question=request.question,
        mode=request.mode,
        classification=classification,
        answer_status=status,
        sections=sections,
        evidences=evidences,
        citations=citations,
        warnings=warnings,
        trace=RetrievalTrace(
            query_expansions=expansions,
            channels=channels,
            candidates=len(industry_retriever.hybrid.catalog) + paper_candidates,
            selected=len(evidences),
            external_status=external_status,
        ),
    )


@app.get(f"{settings.api_prefix}/papers/search", response_model=PaperSearchResponse)
async def search_papers(
    q: str = Query(min_length=2, max_length=500),
    limit: int = Query(default=10, ge=1, le=25),
) -> PaperSearchResponse:
    results, status = await paper_retriever.search(q, limit)
    return PaperSearchResponse(query=q, results=results, provider_status=status)


@app.get(f"{settings.api_prefix}/papers/detail", response_model=PaperResult)
async def paper_detail(source: str, paper_id: str) -> PaperResult:
    result = await paper_retriever.detail(source, paper_id)
    if not result:
        raise HTTPException(status_code=404, detail="Paper metadata was not found at the selected provider.")
    return result


@app.get(f"{settings.api_prefix}/concepts", response_model=list[ConceptSummary])
async def concepts(q: str = "", category: str | None = None) -> list[ConceptSummary]:
    return concept_retriever.search(q, category)


@app.get(f"{settings.api_prefix}/concepts/{{concept_id}}", response_model=ConceptSummary)
async def concept_detail(concept_id: str) -> ConceptSummary:
    result = concept_retriever.get(concept_id)
    if not result:
        raise HTTPException(status_code=404, detail="Concept not found")
    return result
