from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class QuestionCategory(StrEnum):
    TERM = "TERM"
    ENGINEERING_PROBLEM = "ENGINEERING_PROBLEM"
    RESEARCH_QUESTION = "RESEARCH_QUESTION"
    PAPER_SEARCH = "PAPER_SEARCH"
    RTL_QUESTION = "RTL_QUESTION"
    STA = "STA"
    CDC = "CDC"
    RDC = "RDC"
    VERIFICATION = "VERIFICATION"
    SYNTHESIS = "SYNTHESIS"
    LOW_POWER = "LOW_POWER"
    DFT = "DFT"
    PHYSICAL_DESIGN = "PHYSICAL_DESIGN"
    ARCHITECTURE = "ARCHITECTURE"


class AnswerMode(StrEnum):
    ENGINEERING = "engineering"
    RESEARCH = "research"
    LEARNING = "learning"


class UILanguage(StrEnum):
    ZH = "zh"
    EN = "en"


class EvidenceLevel(StrEnum):
    INDUSTRY_ESTABLISHED = "Industry Established"
    RESEARCH_SUPPORTED = "Research Supported"
    EMERGING_RESEARCH = "Emerging Research"
    ENGINEERING_HEURISTIC = "Engineering Heuristic"
    EXPERIMENTAL = "Experimental"


class Classification(BaseModel):
    category: QuestionCategory
    confidence: float = Field(ge=0, le=1)
    signals: list[str] = []


class Evidence(BaseModel):
    source_id: str
    title: str
    source: str
    document_type: str
    url: HttpUrl
    year: int | None = None
    authors: list[str] = []
    venue: str | None = None
    doi: str | None = None
    citation_count: int = 0
    open_access: bool = False
    excerpt: str
    domains: list[str] = []
    authority_score: float = Field(ge=0, le=1)
    engineering_applicability: float = Field(ge=0, le=1)
    evidence_level: EvidenceLevel
    relevance: float = Field(default=0, ge=0, le=1)
    score: float = Field(default=0, ge=0, le=1)
    metadata: dict[str, Any] = {}


class AnswerSection(BaseModel):
    key: str
    title: str
    content: str
    source_ids: list[str] = []
    code: str | None = None


class Citation(BaseModel):
    number: int
    source_id: str
    title: str
    url: HttpUrl


class RetrievalTrace(BaseModel):
    query_expansions: list[str]
    channels: list[str]
    candidates: int
    selected: int
    external_status: dict[str, str] = {}


class ResearchRequest(BaseModel):
    question: str = Field(min_length=4, max_length=2000)
    mode: AnswerMode = AnswerMode.ENGINEERING
    language: UILanguage = UILanguage.ZH
    max_evidence: int = Field(default=6, ge=1, le=12)


class ResearchResponse(BaseModel):
    question: str
    mode: AnswerMode
    classification: Classification
    answer_status: str
    sections: list[AnswerSection]
    evidences: list[Evidence]
    citations: list[Citation]
    warnings: list[str] = []
    trace: RetrievalTrace


class PaperResult(BaseModel):
    paper_id: str
    title: str
    abstract: str | None = None
    authors: list[str] = []
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    citation_count: int = 0
    url: HttpUrl
    source: str
    open_access: bool = False


class PaperSearchResponse(BaseModel):
    query: str
    results: list[PaperResult]
    provider_status: dict[str, str]


class ConceptSummary(BaseModel):
    id: str
    name: str
    abbreviation: str | None = None
    chinese_name: str
    definition: str
    definition_en: str | None = None
    category: str
    related: list[str] = []
