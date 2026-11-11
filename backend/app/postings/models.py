import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.db_types import created_at, uuid_pk


class Posting(Base):
    __tablename__ = "postings"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    source: Mapped[str] = mapped_column(String(20))
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    catalog_posting_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    company: Mapped[str] = mapped_column(String(200), default="")
    title: Mapped[str] = mapped_column(String(300), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    description_text: Mapped[str] = mapped_column(Text)
    requirements: Mapped[list] = mapped_column(JSONB, default=list)
    seniority: Mapped[str] = mapped_column(String(20), default="unknown")
    created_at: Mapped[datetime] = created_at()
