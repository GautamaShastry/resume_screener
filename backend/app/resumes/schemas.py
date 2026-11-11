import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version_no: int
    source: str
    file_type: str
    parse_status: str
    created_at: datetime


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    archived: bool
    created_at: datetime
    versions: list[VersionSummary]


class VersionOut(VersionSummary):
    resume_id: uuid.UUID
    structured: dict | None
    ats_report: dict | None


class ResumeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    archived: bool | None = None


class UploadOut(BaseModel):
    task_id: uuid.UUID
    resume_id: uuid.UUID
    resume_version_id: uuid.UUID
