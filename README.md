# HireReady

Résumé ↔ job fit analysis with evidence, grounded tailoring, application tracking, interview practice, and job recommendations.

- Design: `docs/superpowers/specs/2026-11-10-hireready-v2-design.md`
- v1 code: tag `v1-legacy`

## Local development

```bash
docker compose up -d postgres azurite
cd backend && python -m venv .venv && . .venv/Scripts/activate && pip install -e ".[dev]"
alembic upgrade head && uvicorn app.main:build_app --factory --reload
# second shell
cd backend && python -m app.worker
# third shell
cd frontend && npm install && npm run dev
```
