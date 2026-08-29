import uuid
from datetime import date, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(primary_key=True, default=uuid.uuid4)


paper_authors = Table(
    "paper_authors",
    Base.metadata,
    Column("paper_id", ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
    Column("author_order", Integer, nullable=False, default=0),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Paper(Base):
    __tablename__ = "papers"
    id: Mapped[uuid.UUID] = uuid_pk()
    external_id: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None]
    venue: Mapped[str | None] = mapped_column(String(300))
    doi: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    citation_count: Mapped[int] = mapped_column(default=0)
    url: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(80))
    open_access: Mapped[bool] = mapped_column(Boolean, default=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    authors: Mapped[list["Author"]] = relationship(secondary=paper_authors, back_populates="papers")


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(240), index=True)
    external_id: Mapped[str | None] = mapped_column(String(160), unique=True)
    papers: Mapped[list[Paper]] = relationship(secondary=paper_authors, back_populates="authors")


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(Text)
    filename: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(120))
    sha256: Mapped[str] = mapped_column(String(64), unique=True)
    parse_status: Mapped[str] = mapped_column(String(40), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index"),)
    id: Mapped[uuid.UUID] = uuid_pk()
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    section: Mapped[str | None] = mapped_column(String(200))
    chunk_index: Mapped[int]
    page_start: Mapped[int | None]
    page_end: Mapped[int | None]
    text: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int | None]
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))


class IndustrySource(Base):
    __tablename__ = "industry_sources"
    id: Mapped[uuid.UUID] = uuid_pk()
    source_id: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    company: Mapped[str] = mapped_column(String(160), index=True)
    document_type: Mapped[str] = mapped_column(String(100), index=True)
    domain: Mapped[str] = mapped_column(String(100), index=True)
    publish_date: Mapped[date | None] = mapped_column(Date)
    url: Mapped[str] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text)
    authority_score: Mapped[float] = mapped_column(Float)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Concept(Base):
    __tablename__ = "concepts"
    id: Mapped[uuid.UUID] = uuid_pk()
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(240), index=True)
    abbreviation: Mapped[str | None] = mapped_column(String(40), index=True)
    chinese_name: Mapped[str] = mapped_column(String(240), index=True)
    definition: Mapped[str] = mapped_column(Text)
    detailed_explanation: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), index=True)
    equations: Mapped[list[Any]] = mapped_column(JSON, default=list)
    examples: Mapped[list[Any]] = mapped_column(JSON, default=list)
    common_mistakes: Mapped[list[Any]] = mapped_column(JSON, default=list)
    engineering_usage: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))


class ConceptRelation(Base):
    __tablename__ = "concept_relations"
    __table_args__ = (UniqueConstraint("source_id", "target_id", "relation_type"),)
    id: Mapped[uuid.UUID] = uuid_pk()
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), index=True)
    relation_type: Mapped[str] = mapped_column(String(50), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    evidence_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)


class Solution(Base):
    __tablename__ = "solutions"
    id: Mapped[uuid.UUID] = uuid_pk()
    problem: Mapped[str] = mapped_column(Text, index=True)
    domain: Mapped[str] = mapped_column(String(100), index=True)
    design_stage: Mapped[str] = mapped_column(String(100), index=True)
    symptom: Mapped[str] = mapped_column(Text)
    root_cause: Mapped[str] = mapped_column(Text)
    recommended_solution: Mapped[str] = mapped_column(Text)
    alternative_solution: Mapped[str | None] = mapped_column(Text)
    conditions: Mapped[str] = mapped_column(Text)
    advantages: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    disadvantages: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    verification_method: Mapped[str] = mapped_column(Text)
    eda_tools: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    evidence_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    confidence_score: Mapped[float] = mapped_column(Float)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), index=True)
    mode: Mapped[str] = mapped_column(String(40))
    classification_confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[uuid.UUID] = uuid_pk()
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(50))
    sections: Mapped[list[Any]] = mapped_column(JSON)
    retrieval_trace: Mapped[dict[str, Any]] = mapped_column(JSON)
    model_name: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Citation(Base):
    __tablename__ = "citations"
    __table_args__ = (UniqueConstraint("answer_id", "citation_number"),)
    id: Mapped[uuid.UUID] = uuid_pk()
    answer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("answers.id", ondelete="CASCADE"), index=True)
    citation_number: Mapped[int]
    source_id: Mapped[str] = mapped_column(String(180), index=True)
    source_type: Mapped[str] = mapped_column(String(60))
    title_snapshot: Mapped[str] = mapped_column(Text)
    url_snapshot: Mapped[str] = mapped_column(Text)


class Collection(Base):
    __tablename__ = "collections"
    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    is_private: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CollectionItem(Base):
    __tablename__ = "collection_items"
    __table_args__ = (UniqueConstraint("collection_id", "item_type", "item_id"),)
    id: Mapped[uuid.UUID] = uuid_pk()
    collection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("collections.id", ondelete="CASCADE"), index=True)
    item_type: Mapped[str] = mapped_column(String(50))
    item_id: Mapped[str] = mapped_column(String(180))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
