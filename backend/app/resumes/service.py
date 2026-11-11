import uuid

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.errors import ValidationFailed
from app.core.services import Services
from app.quotas.service import check_quota
from app.resumes.extract import sniff_type
from app.resumes.models import Resume, ResumeVersion
from app.tasks.service import create_task

MAX_BYTES = 5 * 1024 * 1024
CONTENT_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


async def read_upload(file: UploadFile) -> tuple[bytes, str]:
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValidationFailed("File is larger than 5 MB.")
    file_type = sniff_type(data)
    if file_type is None:
        raise ValidationFailed("Upload a PDF or DOCX file.")
    return data, file_type


async def add_version(
    session: AsyncSession,
    services: Services,
    user: User,
    resume: Resume,
    data: bytes,
    file_type: str,
) -> tuple[ResumeVersion, uuid.UUID]:
    await check_quota(session, services.settings, user.id, "resume_upload")
    max_no = (
        await session.execute(
            select(func.coalesce(func.max(ResumeVersion.version_no), 0)).where(
                ResumeVersion.resume_id == resume.id
            )
        )
    ).scalar_one()
    version = ResumeVersion(
        id=uuid.uuid4(),
        resume_id=resume.id,
        user_id=user.id,
        version_no=max_no + 1,
        source="upload",
        file_type=file_type,
        parse_status="pending",
        blob_path="",
    )
    version.blob_path = f"resumes/{user.id}/{version.id}.{file_type}"
    await services.blob.put(version.blob_path, data, CONTENT_TYPES[file_type])
    session.add(version)
    await session.commit()
    task = await create_task(
        session,
        services.queue,
        user_id=user.id,
        type="resume.parse",
        input={"resume_version_id": str(version.id)},
    )
    return version, task.id


async def delete_resume(session: AsyncSession, services: Services, resume: Resume) -> None:
    for version in resume.versions:
        await services.blob.delete(version.blob_path)
    await session.delete(resume)
    await session.commit()
