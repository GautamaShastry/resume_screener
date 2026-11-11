from datetime import date

import pytest

from app.core.errors import QuotaExceeded
from app.quotas import service
from app.quotas.service import check_quota, consume, usage_today


async def test_consume_accumulates_and_check_enforces(db_session, make_user, settings):
    user = await make_user()
    settings.quota_limits["analysis"] = 2
    await check_quota(db_session, settings, user.id, "analysis")
    await consume(db_session, user.id, "analysis")
    await consume(db_session, user.id, "analysis")
    await db_session.commit()
    with pytest.raises(QuotaExceeded) as exc:
        await check_quota(db_session, settings, user.id, "analysis")
    assert exc.value.details["limit"] == 2
    assert exc.value.details["used"] == 2
    assert exc.value.details["resets_at"].endswith("+00:00")


async def test_check_counts_requested_amount(db_session, make_user, settings):
    user = await make_user()
    settings.quota_limits["analysis"] = 3
    await consume(db_session, user.id, "analysis", 2)
    await db_session.commit()
    with pytest.raises(QuotaExceeded):
        await check_quota(db_session, settings, user.id, "analysis", n=2)


async def test_new_day_resets(db_session, make_user, settings, monkeypatch):
    user = await make_user()
    settings.quota_limits["analysis"] = 1
    monkeypatch.setattr(service, "utc_today", lambda: date(2026, 1, 1))
    await consume(db_session, user.id, "analysis")
    await db_session.commit()
    monkeypatch.setattr(service, "utc_today", lambda: date(2026, 1, 2))
    await check_quota(db_session, settings, user.id, "analysis")


async def test_usage_today_lists_all_kinds(db_session, make_user, settings):
    user = await make_user()
    await consume(db_session, user.id, "resume_upload")
    await db_session.commit()
    usage = await usage_today(db_session, settings, user.id)
    assert usage["resume_upload"] == {"used": 1, "limit": 10}
    assert usage["analysis"] == {"used": 0, "limit": 20}
