import uuid

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import current_user
from app.auth.models import User
from app.core.deps import get_services, get_session
from app.core.ownership import get_owned
from app.core.services import Services
from app.resumes.models import Resume, ResumeVersion
from app.resumes.schemas import ResumeOut, ResumeUpdate, UploadOut, VersionOut
from app.resumes.service import CONTENT_TYPES, add_version, delete_resume, read_upload

router = APIRouter(prefix="/api", tags=["resumes"])


@router.get("/resumes", response_model=list[ResumeOut])
async def list_resumes(
    user: User = Depends(current_user), session: AsyncSession = Depends(get_session)
) -> list[Resume]:
    stmt = select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc())
    return list((await session.execute(stmt)).scalars())


@router.post("/resumes", response_model=UploadOut, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(
    file: UploadFile = File(...),
    title: str = Form(..., min_length=1, max_length=200),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    services: Services = Depends(get_services),
) -> UploadOut:
    data, file_type = await read_upload(file)
    resume = Resume(user_id=user.id, title=title)
    session.add(resume)
    await session.flush()
    version, task_id = await add_version(session, services, user, resume, data, file_type)
    return UploadOut(task_id=task_id, resume_id=resume.id, resume_version_id=version.id)


@router.get("/resumes/{resume_id}", response_model=ResumeOut)
async def get_resume(
    resume_id: uuid.UUID,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> Resume:
    return await get_owned(session, Resume, resume_id, user.id)


@router.patch("/resumes/{resume_id}", response_model=ResumeOut)
async def update_resume(
    resume_id: uuid.UUID,
    body: ResumeUpdate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> Resume:
    resume = await get_owned(session, Resume, resume_id, user.id)
    if body.title is not None:
        resume.title = body.title
    if body.archived is not None:
        resume.archived = body.archived
    await session.commit()
    return resume


@router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_resume(
    resume_id: uuid.UUID,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    services: Services = Depends(get_services),
) -> Response:
    resume = await get_owned(session, Resume, resume_id, user.id)
    await delete_resume(session, services, resume)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/resumes/{resume_id}/versions",
    response_model=UploadOut,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_version(
    resume_id: uuid.UUID,
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    services: Services = Depends(get_services),
) -> UploadOut:
    resume = await get_owned(session, Resume, resume_id, user.id)
    data, file_type = await read_upload(file)
    version, task_id = await add_version(session, services, user, resume, data, file_type)
    return UploadOut(task_id=task_id, resume_id=resume.id, resume_version_id=version.id)


@router.get("/resume-versions/{version_id}", response_model=VersionOut)
async def get_version(
    version_id: uuid.UUID,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
) -> ResumeVersion:
    return await get_owned(session, ResumeVersion, version_id, user.id)


@router.get("/resume-versions/{version_id}/download")
async def download_version(
    version_id: uuid.UUID,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    services: Services = Depends(get_services),
) -> Response:
    version = await get_owned(session, ResumeVersion, version_id, user.id)
    data = await services.blob.get(version.blob_path)
    filename = f"resume-v{version.version_no}.{version.file_type}"
    return Response(
        content=data,
        media_type=CONTENT_TYPES[version.file_type],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
