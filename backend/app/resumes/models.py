import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.db_types import created_at, uuid_pk


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    archived: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = created_at()

    versions: Mapped[list["ResumeVersion"]] = relationship(
        order_by="ResumeVersion.version_no", lazy="selectin", passive_deletes=True
    )


class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    __table_args__ = (UniqueConstraint("resume_id", "version_no"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    version_no: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(20))  # upload | tailored
    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True
    )
    tailored_for_posting_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("postings.id", ondelete="SET NULL"), nullable=True
    )
    blob_path: Mapped[str] = mapped_column(String(400))
    file_type: Mapped[str] = mapped_column(String(10))  # pdf | docx
    parse_status: Mapped[str] = mapped_column(
        String(20), default="pending", server_default="pending"
    )  # pending | ready | failed
    text: Mapped[str] = mapped_column(Text, default="", server_default="")
    structured: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ats_report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = created_at()
