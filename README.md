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

## Tests
- Backend: `cd backend && pytest -q` (needs `docker compose up -d postgres azurite`)
- Frontend: `cd frontend && npm test`
- End-to-end: `docker compose up -d --build && cd frontend && npm run e2e`

## API types
After changing backend routes or schemas:
`cd backend && python -m app.scripts.export_openapi > ../frontend/openapi.json && cd ../frontend && npm run gen:api`

## Deployment
See `docs/runbook.md`. Pushes to `main` deploy automatically.
