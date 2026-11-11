from sqlalchemy import select

from app.resumes.models import Resume, ResumeVersion


async def test_user_delete_cascades(db_session, make_user):
    user = await make_user("cascade@example.com")
    resume = Resume(user_id=user.id, title="Backend")
    db_session.add(resume)
    await db_session.flush()
    db_session.add(
        ResumeVersion(
            resume_id=resume.id,
            user_id=user.id,
            version_no=1,
            source="upload",
            blob_path="x",
            file_type="pdf",
        )
    )
    await db_session.commit()

    await db_session.delete(user)
    await db_session.commit()

    assert (await db_session.execute(select(ResumeVersion))).first() is None
    assert (await db_session.execute(select(Resume))).first() is None
