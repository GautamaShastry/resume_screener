import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.postings.schemas import Requirement


class Quote(BaseModel):
    bullet_id: str
    text: str


class EvidenceItem(BaseModel):
    requirement_id: str
    status: Literal["met", "partial", "missing"]
    quotes: list[Quote]
    note: str


class Project(BaseModel):
    title: str
    scope: str
    deliverables: list[str]
    resume_bullet: str


class GapItem(BaseModel):
    requirement_id: str
    type: Literal["not_stated", "real_gap"]
    related_bullet_ids: list[str]
    related_quotes: list[Quote]
    suggested_bullet: str | None
    project: Project | None


class ScoreBreakdown(BaseModel):
    coverage: float
    seniority_fit: int
    must_missing_count: int
    capped: bool
    years_experience: float
    weights: dict[str, int]


class PostingRef(BaseModel):
    id: uuid.UUID
    title: str
    company: str
    location: str
    source_url: str | None


class VersionRef(BaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    version_no: int
    resume_title: str


class AnalysisCreate(BaseModel):
    resume_version_id: uuid.UUID
    posting_id: uuid.UUID
    force: bool = False


class AnalysisStartOut(BaseModel):
    analysis_id: uuid.UUID | None = None
    task_id: uuid.UUID | None = None


class AnalysisSummary(BaseModel):
    id: uuid.UUID
    score: int
    created_at: datetime
    posting: PostingRef
    resume_version: VersionRef


class AnalysisOut(AnalysisSummary):
    score_breakdown: ScoreBreakdown
    requirements: list[Requirement]
    evidence: list[EvidenceItem]
    gaps: list[GapItem]
