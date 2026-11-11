import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Requirement(BaseModel):
    id: str
    text: str
    kind: Literal["must", "nice"]
    category: str
    source_phrase: str


class PostingCreate(BaseModel):
    url: str | None = Field(default=None, max_length=2000)
    text: str | None = Field(default=None, min_length=100, max_length=50_000)
    title: str | None = Field(default=None, max_length=300)
    company: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def _exactly_one(self) -> "PostingCreate":
        if (self.url is None) == (self.text is None):
            raise ValueError("Provide either a URL or the job description text")
        return self


class PostingSummary(BaseModel):
    id: uuid.UUID
    title: str
    company: str
    location: str
    source: str
    source_url: str | None
    requirements_count: int
    created_at: datetime


class PostingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company: str
    location: str
    source: str
    source_url: str | None
    seniority: str
    description_text: str
    requirements: list[Requirement]
    created_at: datetime
