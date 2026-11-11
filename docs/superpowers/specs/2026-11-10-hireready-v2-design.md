# HireReady v2 — Design Spec

**Date:** 2026-11-10
**Status:** Draft for review
**Replaces:** v1 (React + Spring Boot + Flask "10-agent" pipeline), tagged `v1-legacy`

---

## 1. Goal and scope

HireReady v2 is a public web app for **job seekers**. It helps a user understand how well their résumé fits a job, improve the résumé for that job without inventing anything, track applications, practice interviews, and find more jobs to apply to.

### Product decisions (agreed)
| Decision | Choice |
|---|---|
| Target user | Job seekers only. Recruiter features (recruiter notes, interview scheduler, fairness auditor, candidate ranking for recruiters) are removed. |
| Backend | Single **FastAPI** (Python) codebase. Spring Boot and Flask are retired. |
| LLM | **Azure OpenAI** (chat + embeddings) via managed identity, behind an `LLMClient` interface. |
| Auth | **Microsoft Entra External ID** (Google + email sign-in, verification, password reset hosted by Entra). |
| Frontend | **React + Vite + TypeScript**, Tailwind, TanStack Query, typed client generated from OpenAPI. |
| Monetization | Free with **per-user daily quotas**; `users.plan` column reserved for future paid tiers. |
| Background work | **Azure Storage Queue + separate worker container** (same image). |
| Job recommendations source | Own **catalog crawled from public Greenhouse / Lever / Ashby job boards**. |
| Data migration | None. Fresh database; v1 code removed after tagging. |

### Features
1. **Résumé library** with immutable versions and an **ATS parse preview**.
2. **Job import** from URL (Greenhouse/Lever/Ashby APIs, generic HTML) or pasted text.
3. **Evidence-based match**: every requirement mapped to quoted résumé bullets; deterministic score.
4. **Gap analysis**: "not stated" vs "real gap", with suggested bullets or a proof-of-skill project.
5. **Grounded tailoring**: rewrites using only résumé facts and user answers; DOCX/PDF export as a new version.
6. **Where should I apply**: rank up to 10 jobs for one résumé version.
7. **Application tracker** with analytics on response rate by résumé version, score bucket, and tailoring.
8. **Interview practice** targeted at the user's gaps, with STAR feedback and retries.
9. **Job recommendations**: top 5 jobs from the catalog for a (tailored) résumé version, each with a full analysis.

### Success criteria
A deployed app on Azure where a new user can sign up, upload a résumé, see its ATS report, import a job, get an evidence-backed analysis, tailor and export a résumé, re-analyze it to see the score change, get 5 job recommendations, track applications and see analytics, and practice interview answers — with no cross-user data access, and quotas enforced.

### Non-goals (v2)
Recruiter workflows; paid plans/billing; email or calendar integration; browser extension; voice interview practice; scraping LinkedIn/Indeed; preserving the original résumé's visual layout on export; multi-environment (staging) backend.

---

## 2. Architecture

```
                 ┌──────────────┐
   User ───────► │   Website    │ ◄──── Entra External ID (sign-in)
                 │ (Static Web  │
                 │    Apps)     │
                 └──────┬───────┘
                        │ HTTPS + Bearer token, SSE for progress
                        ▼
                 ┌──────────────┐  enqueue {taskId}  ┌──────────────┐
                 │  api (FastAPI│ ─────────────────► │ Storage Queue│
                 │ Container App│                    │   "tasks"    │
                 └──┬───────────┘                    └──────┬───────┘
                    │ read/write                            │ receive
                    ▼                                       ▼
              ┌──────────────┐  progress + results  ┌──────────────┐
              │  Postgres    │ ◄─────────────────── │   worker     │ ──► Azure OpenAI
              │ (+ pgvector) │                      │ Container App│
              └──────▲───────┘                      └──────┬───────┘
                     │ upsert postings                     │
              ┌──────┴───────┐                      ┌──────▼───────┐
              │   crawler    │                      │ Blob Storage │
              │ (Container   │                      │  (files)     │
              │  Apps Job,   │                      └──────────────┘
              │  every 6h)   │
              └──────────────┘
```

- **api**: handles all synchronous requests; never calls the LLM for long work. Min 1 replica.
- **worker**: same image, entrypoint `python -m app.worker`; processes queued tasks. Scales 0–3 on queue length (KEDA `azure-queue` scaler).
- **crawler**: same image, entrypoint `python -m app.crawler`; Container Apps Job on cron `0 */6 * * *`.
- **migrations**: same image, `alembic upgrade head`; Container Apps Job run once per deployment.

### Repository layout
```
backend/
  app/
    core/        settings (pydantic-settings), db session, logging, errors, telemetry
    auth/        Entra JWT validation, current_user dependency, dev auth (non-prod only)
    llm/         LLMClient interface, AzureOpenAIClient, FakeLLM, prompt templates
    storage/     BlobStore interface: AzureBlobStore, LocalBlobStore
    tasks/       TaskQueue interface (AzureQueue, InMemoryQueue), task service, SSE endpoint, worker loop
    quotas/      quota check/consume
    resumes/     upload, extraction, structuring, ATS checks, versions
    postings/    URL import (source adapters), paste, requirement extraction
    analysis/    evidence, scoring, gaps, ranking
    tailoring/   propose, refine, no-invention check, export (DOCX/PDF)
    tracker/     applications, events, analytics queries
    practice/    question generation, grading
    catalog/     companies, crawler, embeddings, recommendations
    main.py      FastAPI app; worker.py; crawler.py
  migrations/    Alembic
  tests/
frontend/        React + Vite + TS
infra/           Bicep modules + main.bicep + parameters
docs/            specs, runbook
.github/workflows/
docker-compose.yml   postgres(pgvector), azurite, api, worker
```

Module rule: each feature module owns its router, service, schemas, and models; modules call each other only through service functions. Each AI feature is a **task handler** registered with the worker.

---

## 3. Data model

All IDs are UUIDv4. All user-owned tables have `user_id` and every query filters by it. Timestamps are `timestamptz`. Schema managed by Alembic.

| Table | Columns | Notes |
|---|---|---|
| `users` | id, entra_oid (unique), email, name, plan (default `free`), created_at | Upserted on first authenticated request. |
| `user_preferences` | user_id (PK), target_roles text[], locations text[], remote_ok bool, seniority, exclude_companies uuid[], exclude_keywords text[] | Used by recommendations. |
| `resumes` | id, user_id, title, archived, created_at | A library entry; groups versions. |
| `resume_versions` | id, resume_id, user_id, version_no, source (`upload`/`tailored`), parent_version_id, tailored_for_posting_id, blob_path, file_type (`pdf`/`docx`), text, structured jsonb, ats_report jsonb, embedding vector, created_at | **Immutable** after creation. `embedding` filled lazily for recommendations. |
| `postings` | id, user_id, source (`greenhouse`/`lever`/`ashby`/`html`/`paste`/`catalog`), source_url, catalog_posting_id, company, title, location, description_text, requirements jsonb, seniority, created_at | User-owned copy; catalog jobs are copied here when recommended. |
| `analyses` | id, user_id, resume_version_id, posting_id, score, score_breakdown jsonb, evidence jsonb, gaps jsonb, batch_id, model, prompt_version, created_at | Latest analysis per (version, posting) is reused unless forced. |
| `tailoring_sessions` | id, user_id, analysis_id, base_version_id, status (`proposing`/`review`/`refining`/`exported`), questions jsonb, suggestions jsonb, refine_count, result_version_id, created_at | |
| `applications` | id, user_id, posting_id, resume_version_id, analysis_id, stage, applied_at, notes, updated_at | Stages: `saved`, `applied`, `screening`, `interview`, `offer`, `rejected`, `withdrawn`. One per (user, posting). |
| `application_events` | id, application_id, from_stage, to_stage, at | Analytics source. |
| `practice_sessions` | id, user_id, analysis_id, created_at | |
| `practice_questions` | id, session_id, question, category (`deep_dive`/`gap`/`behavioral`), requirement_id, bullet_id, attempts jsonb | `attempts`: list of `{answer, feedback, at}`. |
| `companies` | id, name, ats, board_token, active, consecutive_failures, added_by_user_id, created_at | Seeded from `backend/app/catalog/companies.yaml`. Unique (ats, board_token). |
| `catalog_postings` | id, company_id, external_id, title, location, remote, department, url, description_text, content_hash, requirements jsonb, seniority, embedding vector(1536), first_seen, last_seen, closed_at | Unique (company_id, external_id). HNSW index on embedding (cosine). |
| `recommendations` | id, user_id, resume_version_id, catalog_posting_id, posting_id, analysis_id, rank, feedback (`none`/`not_interested`/`tracked`), created_at | |
| `tasks` | id, user_id, type, status (`queued`/`running`/`succeeded`/`failed`), input jsonb, progress jsonb, result_ref jsonb, error_code, error_message, attempts, tokens_in, tokens_out, created_at, started_at, finished_at | |
| `usage` | (user_id, day, kind) PK, count | Daily quotas (UTC day). |

### JSON shapes
- `resume_versions.structured`:
  `{contact:{name,email,phone,location,links[]}, summary:{id,text}|null, skills:[{id,text}], sections:[{id, kind:"experience"|"education"|"projects"|"other", title, entries:[{id, org, role, start, end, location, bullets:[{id,text}]}]}]}`
  Bullet IDs are assigned by the server (`b1`, `b2`, … unique within the version).
- `resume_versions.ats_report`: `{checks:[{check, severity:"error"|"warning"|"info", message, how_to_fix}], parsed_view:{text, fields:{name,email,phone,sections[]}}}`
- `postings.requirements` / `catalog_postings.requirements`: `[{id:"r1", text, kind:"must"|"nice", category:"skill"|"experience"|"education"|"other", source_phrase}]`
- `analyses.evidence`: `[{requirement_id, status:"met"|"partial"|"missing", quotes:[{bullet_id, text}], note}]`
- `analyses.score_breakdown`: `{coverage, seniority_fit, must_missing_count, capped:bool, weights:{must:3,nice:1}}`
- `analyses.gaps`: `[{requirement_id, type:"not_stated"|"real_gap", related_bullet_ids[], suggested_bullet|null, project:{title, scope, deliverables[], resume_bullet}|null}]`
- `tailoring_sessions.suggestions`: `[{id, kind:"rewrite"|"add"|"summary"|"skills_order", bullet_id|null, original|null, proposed, targets:[requirement_id], grounded_in:[bullet_id|answer_id], requires_confirmation:bool, decision:"pending"|"accepted"|"rejected"|"edited", final_text|null}]`
- `tailoring_sessions.questions`: `[{id:"q1", bullet_id, question, answer|null}]`
- `practice_questions.attempts[].feedback`: `{scores:{situation,task,action,result,relevance,specificity} (1–5), strengths[], improvements[], improved_answer}`
- `tasks.progress`: `{step, steps:[...], percent}`

### Data rules
- Résumé versions never change; tailoring always creates a new version.
- Deleting a résumé, posting, or account cascades to dependent rows and deletes associated blobs.
- Catalog tables are global (not user-owned); user interaction with a catalog job always goes through a user-owned `postings` copy.

---

## 4. Task system

**Lifecycle**
1. API checks quota → inserts `tasks` row (`queued`) → sends `{taskId}` to queue `tasks` → returns `202 {taskId}`.
2. Worker receives message (visibility timeout 5 min, renewed every 2 min while running) → claims via `UPDATE tasks SET status='running', started_at=now(), attempts=attempts+1 WHERE id=:id AND status='queued'`. If 0 rows updated, delete message and stop.
3. Handler runs, calling `progress(step)` after each step (writes `tasks.progress`).
4. Handler writes all results in **one transaction** together with `status='succeeded'`, `result_ref`, token counts, and quota consumption. Message deleted.
5. On exception: status reset to `queued` and the message is left to reappear (retry). On the 3rd failed attempt (`dequeue_count >= 3`) → message moved to `tasks-poison`, task `failed` with `error_code`.
6. Worker startup: tasks stuck `running` for >15 min are reset to `queued` and re-enqueued.

**Progress to browser**: `GET /tasks/{id}/events` (SSE) polls the row every 1s, emits `progress` events on change and a final `done`/`failed` event, closes after terminal state or 10 min.

**Task types**

| Type | Input | Steps |
|---|---|---|
| `resume.parse` | resume_version_id | extract text → ATS checks → structure → grounding guard |
| `postings.import` | posting_id, url or text | fetch (if URL) → extract requirements |
| `analysis.run` | resume_version_id, posting_id | evidence → seniority → score → gaps |
| `ranking.run` | resume_version_id, urls[], posting_ids[] | import new URLs → analyses (concurrency 3) |
| `tailoring.run` | tailoring_session_id | propose → no-invention check |
| `tailoring.refine` | tailoring_session_id | regenerate bullets affected by answers → no-invention check |
| `practice.generate` | practice_session_id | generate 8 questions |
| `practice.grade` | practice_question_id, answer | grade → append attempt |
| `recommend.run` | resume_version_id | embed résumé → vector search → shortlist 8 → extract requirements (cached) → analyses → top 5 |

### Quotas (defaults, configurable via settings)
| kind | per user per UTC day | consumed by |
|---|---|---|
| `resume_upload` | 10 | `resume.parse` |
| `posting_import` | 30 | `postings.import` (incl. URLs imported inside ranking) |
| `analysis` | 20 | `analysis.run`, each analysis in `ranking.run`; cached results are free |
| `tailoring` | 10 | `tailoring.run` (each session allows max 3 `tailoring.refine`) |
| `practice_session` | 5 | `practice.generate` |
| `practice_answer` | 30 | `practice.grade` |
| `recommendation` | 3 | `recommend.run` (its internal analyses are not counted) |

Quota is checked at enqueue (reject with `429 QUOTA_EXCEEDED`, `details.resets_at`) and consumed only on success.

---

## 5. Feature specifications

### 5.1 Résumé upload and ATS parse preview (`resume.parse`)
- **Accept** PDF/DOCX ≤ 5 MB; type verified by magic bytes. Stored at `resumes/{user_id}/{version_id}.{ext}`.
- **Extract text**: PyMuPDF (keeping block coordinates) for PDF; python-docx (body, tables, headers/footers separately) for DOCX.
- **ATS checks** (deterministic):
  | check | rule | severity |
  |---|---|---|
  | `no_text` | < 200 extractable chars per page | error |
  | `multi_column` | PDF text blocks on a page cluster into ≥2 x-ranges that overlap vertically | warning |
  | `tables` | DOCX tables present, or PDF table detection (PyMuPDF `find_tables`) | warning |
  | `header_footer_content` | contact info or text only found in DOCX header/footer or PDF top/bottom 5% margins | warning |
  | `images` | embedded images/icons present | info |
  | `nonstandard_headings` | section headings not matching a known list (Experience, Education, Skills, Projects, Summary, …, with synonyms) | warning |
  | `missing_contact` | no email or no phone found by regex | error |
  | `length` | > 2 pages | info |
  | `date_format` | more than one date format detected in entries | info |
  `parsed_view` shows text in reading order plus extracted fields. UI copy: "Simulates how common ATS parsers read your file."
- **Structure** (LLM): returns the `structured` shape without IDs; server assigns IDs.
- **Grounding guard**: each bullet must fuzzy-match (`rapidfuzz.partial_ratio ≥ 90`) a span of the extracted text; non-matching bullets are dropped and counted in a log metric.
- `no_text` error → task succeeds with ATS report only; `structured` is null and analysis on that version is blocked with a clear message.

### 5.2 Job import (`postings.import`)
- **Source adapters** (detected by URL host):
  - Greenhouse: `boards.greenhouse.io/{token}/jobs/{id}`, `job-boards.greenhouse.io/...` → `https://boards-api.greenhouse.io/v1/boards/{token}/jobs/{id}`
  - Lever: `jobs.lever.co/{company}/{id}` → `https://api.lever.co/v0/postings/{company}/{id}`
  - Ashby: `jobs.ashbyhq.com/{org}/{id}` → `https://api.ashbyhq.com/posting-api/job-board/{org}`, select job `{id}`
  - LinkedIn / Indeed hosts → immediate `422 UNSUPPORTED_SOURCE` with message "Paste the description instead."
  - Other: fetch HTML; prefer JSON-LD `JobPosting`; else `trafilatura` main-text extraction.
- **Fetch guard**: http/https only; resolve DNS and reject private, loopback, link-local, and metadata (169.254.169.254) addresses; re-validate each redirect (max 3); 10 s timeout; 2 MB cap; identifying User-Agent `HireReadyBot/2.0`.
- **Requirement extraction** (LLM) → title, company, location, seniority (`intern`/`junior`/`mid`/`senior`/`staff+`/`unknown`), requirements list. `must` when phrased as required/must/minimum; `nice` for preferred/bonus/plus; unclear defaults to `must`. Each requirement keeps `source_phrase` (verified substring of description; dropped otherwise).
- Pasted text skips fetching.

### 5.3 Evidence-based analysis (`analysis.run`)
1. **Evidence** (LLM): requirements chunked by 15, chunks run in parallel. Input: structured résumé (bullets with IDs) + requirements. Output per requirement: `status`, `bullet_ids[]`, `note`. Server resolves quote text from IDs; unknown IDs dropped; `met`/`partial` with zero valid quotes → `missing`.
2. **Seniority fit** (deterministic): total years from experience entry dates (overlaps merged). Expected ranges: intern/junior 0–2, mid 2–5, senior 5–9, staff+ 8+. Within range → 100; off by ≤1 year → 50; else 0; `unknown` → 100.
3. **Score** (deterministic):
   - weight: must 3, nice 1; value: met 1, partial 0.5, missing 0
   - `coverage = Σ(weight×value) / Σ(weight)`
   - `score = round(85×coverage + 15×seniority_fit/100)`
   - if any `must` is `missing`: `score = min(score, 75)`, `capped=true`
4. **Gaps** (LLM, after evidence): for each `missing`/`partial` requirement → `not_stated` (with `related_bullet_ids`, `suggested_bullet`, always flagged "confirm this is true") or `real_gap` (with `project`: title, ~2-week scope, deliverables, résumé bullet once done).
- **Caching**: if an analysis exists for (resume_version_id, posting_id) and `force` is false, return it with no task and no quota.

### 5.4 Where should I apply (`ranking.run`)
Input: one résumé version + up to 10 items (URLs and/or posting IDs). Imports new URLs, then runs analyses (concurrency 3) sharing one `batch_id`. Result view: postings sorted by score with top 2 missing must-haves each. Partial failure (one URL fails) does not fail the batch; failed items listed with reason.

### 5.5 Grounded tailoring
- **Start**: `POST /analyses/{id}/tailoring` creates a session and enqueues `tailoring.run`.
- **Propose** (LLM): up to 12 `rewrite` suggestions targeting requirements; one `summary` rewrite; one `skills_order` (only skills with evidence); one `add` per `not_stated` gap (`requires_confirmation=true`). Plus up to 5 `questions` asking for facts that would strengthen specific bullets.
- **No-invention check** (deterministic, applied to every proposal): extract numbers/percentages/currency, and capitalized or known-technology tokens (matched against a skills vocabulary) from `proposed`; each must appear in the union of texts referenced by `grounded_in` (bullets and answered questions). Failing suggestions are dropped and logged. Users never see unchecked suggestions.
- **Refine**: user submits answers → `tailoring.refine` regenerates only suggestions for bullets with new answers (answers become `grounded_in` sources `q1`, …). Max 3 refines per session.
- **Review**: user sets each suggestion to accepted/rejected/edited (edited text is user-authored and not checked). `add` suggestions require an explicit "This is true" confirmation to accept.
- **Export** (`POST /tailoring/{id}/export`, synchronous in API): applies accepted changes to the base `structured` → new `resume_version` (`source=tailored`, `parent_version_id`, `tailored_for_posting_id`) → renders DOCX (python-docx) and PDF (ReportLab) from a single-column ATS-safe template → runs ATS checks on generated DOCX → stores blobs. UI notes the original layout is not preserved. Response includes download links and a "Re-analyze" action (creates a forced analysis for the new version; UI shows score delta).

### 5.6 Application tracker and analytics
- Create from a posting, analysis, or recommendation. Default `resume_version_id`: latest version tailored for that posting, else the analyzed version. One application per (user, posting).
- Moving stage writes `application_events`; moving to `applied` sets `applied_at` if empty.
- Stale flag: stage `applied` with no event for > 21 days → UI prompt "No response — mark as rejected?".
- **Analytics** (`GET /analytics`, SQL only):
  - Funnel: count reaching each stage.
  - Response rate = applications that reached `screening` or later ÷ applications that reached `applied`, grouped by: résumé version; score bucket (<50, 50–69, 70–84, 85+, using the linked analysis); tailored vs not.
  - Median days from `applied` to first later stage.
  - Groups with n < 5 flagged `small_sample`.

### 5.7 Interview practice
- `POST /analyses/{id}/practice` → session + `practice.generate`: 8 questions — 3 `deep_dive` (met requirements), 3 `gap` (missing/partial; coaching on honest answers), 2 `behavioral` (from user's bullets). Each linked to `requirement_id` or `bullet_id`.
- `POST /practice/questions/{id}/answers` (answer ≥ 50 chars) → `practice.grade`: scores 1–5 for situation, task, action, result, relevance, specificity; strengths; improvements; `improved_answer` using only facts from the answer and résumé. Appended to `attempts`; unlimited retries within quota.

### 5.8 Job recommendations
- **Catalog**: `companies` seeded from `companies.yaml` (~300 entries: name, ats, board_token). Users can suggest a company (`POST /companies/suggest {careers_url}`): API detects ATS + token, fetches the board once (with fetch guard) to verify, inserts as active.
- **Crawler** (every 6 h): per active company (concurrency 5, retry 2): list jobs via public board API (Greenhouse `boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`, Lever `api.lever.co/v0/postings/{company}?mode=json`, Ashby `api.ashbyhq.com/posting-api/job-board/{org}`); endpoint shapes are pinned by recorded fixtures in tests; upsert `catalog_postings` by (company_id, external_id); update `last_seen`; set `closed_at` for jobs no longer listed. For new or changed (`content_hash`) postings, compute embedding of `title + location + first 2,000 chars of description`. A company failing 5 consecutive runs is set inactive. Crawler logs a run summary and emits a failure metric.
- **`recommend.run`**:
  1. Résumé version embedding (computed from `structured` summary + bullets + skills; cached on the version).
  2. Vector search: top 50 by cosine distance among postings with `closed_at IS NULL` and `last_seen > now() - 48h`, filtered by preferences (locations/remote, excluded companies/keywords) and excluding postings the user dismissed, already tracks, or was recommended in the last 14 days.
  3. Shortlist 8: `0.7 × similarity + 0.3 × title_seniority_fit` (title matches a target role → 1, else 0.5; seniority equal → 1, adjacent → 0.5, else 0).
  4. For shortlisted postings without `requirements`, run requirement extraction and store on the catalog row (shared cache).
  5. Copy each into the user's `postings` (`source=catalog`), run `analysis.run` logic (concurrency 3).
  6. Save top 5 by score as `recommendations` with rank 1–5.
- First run without preferences → UI asks for preferences first (roles, locations, remote).
- **Feedback**: `not_interested` hides that posting permanently; optional `hide_company` adds to `exclude_companies`. Tracking a recommendation sets `feedback=tracked`.
- **Crawler etiquette**: only public job-board APIs; identifying User-Agent; display summary + link to original posting; applications happen on the company site.

---

## 6. API surface

All routes under `/api`, JSON, Bearer auth (except `/health`). Errors: `{code, message, details}`. Cross-user access → `404 NOT_FOUND`.

| Area | Endpoints |
|---|---|
| Me | `GET /me`, `DELETE /me`, `GET/PUT /me/preferences`, `GET /me/usage` |
| Résumés | `GET /resumes`, `POST /resumes` (multipart: file, title; → 202 task), `PATCH/DELETE /resumes/{id}`, `POST /resumes/{id}/versions` (upload new version → 202), `GET /resume-versions/{id}`, `GET /resume-versions/{id}/download?format=original|docx|pdf` (→ short-lived URL) |
| Postings | `GET /postings`, `POST /postings` (`{url}` or `{text}` → 202), `GET/DELETE /postings/{id}` |
| Analyses | `POST /analyses` (`{resume_version_id, posting_id, force}` → 200 existing or 202 task), `GET /analyses`, `GET /analyses/{id}` |
| Ranking | `POST /rankings` (`{resume_version_id, urls[], posting_ids[]}` → 202), `GET /rankings/{batch_id}` |
| Tailoring | `POST /analyses/{id}/tailoring` (→ 202), `GET /tailoring/{id}`, `POST /tailoring/{id}/answers` (→ 202), `PATCH /tailoring/{id}/suggestions/{sid}`, `POST /tailoring/{id}/export` |
| Tracker | `GET/POST /applications`, `PATCH/DELETE /applications/{id}`, `GET /analytics` |
| Practice | `POST /analyses/{id}/practice` (→ 202), `GET /practice/{id}`, `POST /practice/questions/{id}/answers` (→ 202) |
| Recommendations | `POST /recommendations` (`{resume_version_id?}` → 202), `GET /recommendations`, `PATCH /recommendations/{id}` (`{feedback, hide_company}`), `POST /companies/suggest` |
| Tasks | `GET /tasks?active=true`, `GET /tasks/{id}`, `GET /tasks/{id}/events` (SSE) |
| Health | `GET /health` (no auth) |

---

## 7. Frontend

- **Stack**: React, Vite, TypeScript, Tailwind, Radix UI primitives, React Router, TanStack Query, `openapi-typescript` + `openapi-fetch` (types generated in CI from the API's OpenAPI schema; build fails on drift), `@azure/msal-react`, `@microsoft/fetch-event-source` (SSE with Authorization header), dnd-kit, Chart.js.
- **Screens**:
  | Route | Content |
  |---|---|
  | `/` | Public landing; sign in / sign up |
  | `/home` | Primary "paste job URL or text → pick résumé → Analyze"; recent analyses; tracker summary; remaining quota; "Get recommendations" |
  | `/resumes`, `/resumes/:id` | Library, upload, version timeline, ATS report (checks beside "What an ATS sees") |
  | `/jobs`, `/jobs/:id` | Saved postings, import, requirements |
  | `/analyses/:id` | Score + breakdown; requirements table (filter must/nice, status; expandable quotes); gaps panel; actions Tailor / Practice / Track |
  | `/tailor/:id` | Questions panel; suggestion diff list (accept/reject/edit; confirm for adds); export DOCX/PDF; re-analyze with score delta; "Find jobs for this résumé" |
  | `/apply-where` | Up to 10 URLs → ranked table |
  | `/recommendations` | 5 cards: title, company, location/remote, posted age, score, top matches, biggest missing must; Open / Track / Tailor / Not interested |
  | `/tracker` | Board + Analytics tab |
  | `/practice/:id` | Questions, answer editor, feedback with STAR scores, attempt history |
  | `/settings` | Account, preferences, usage, delete account |
- **Shared**: `useTask(taskId)` hook + `TaskStepper` component; global running-tasks indicator and completion toasts; error boundary per section; API error codes mapped to messages (quota shows reset time); responsive (board scrolls horizontally on mobile); keyboard-accessible tables and diffs; status conveyed by icon + text, not color alone.

---

## 8. Security

- Entra JWT validation: signature (JWKS cached, refreshed on unknown `kid`), issuer, audience, expiry. Dev auth provider exists only when `ENV=local`.
- User scoping enforced in data-access helpers; cross-user tests for every resource.
- One user-assigned **managed identity** for Postgres (Entra auth), Blob, Queue, Azure OpenAI, ACR. Key Vault holds only the Postgres admin bootstrap password.
- Blob container private; downloads via user-delegation SAS valid 5 min.
- Fetch guard (§5.2) for all outbound fetches of user-supplied URLs.
- Prompt-injection posture: untrusted text delimited as data; LLM has no tools; schema validation on all outputs; grounding / no-invention checks; React escaping only (no raw HTML rendering).
- CORS restricted to the Static Web App origin; per-user rate limit 60 requests/min (slowapi) in addition to quotas.
- Security headers + CSP in `staticwebapp.config.json`.
- Logs never include résumé or posting text; only IDs and metrics.
- Account deletion removes all user rows and blobs.

---

## 9. Error handling and observability

- Error envelope `{code, message, details}`; domain exceptions map to HTTP codes (`NOT_FOUND` 404, `VALIDATION` 422, `UNSUPPORTED_SOURCE` 422, `QUOTA_EXCEEDED` 429, `RATE_LIMITED` 429, `INTERNAL` 500).
- LLM calls: 60 s timeout; up to 3 retries with exponential backoff on 429/5xx; on schema-validation failure one repair attempt (validation error fed back), then `LLM_BAD_OUTPUT`.
- Task failures: see §4 retry and poison handling; UI shows "Something went wrong — Retry".
- OpenTelemetry (`azure-monitor-opentelemetry`) → Application Insights; trace context propagated in queue messages (`traceparent`) so api → worker traces join.
- Structured JSON logs. Token usage stored per task.
- Alerts: task failure rate > 10% over 1 h; poison queue length > 0; crawler run failure; budget threshold ($30/month default).

---

## 10. Testing

- **Backend unit** (pytest): scoring formula and cap; seniority fit; no-invention check; ATS checks with fixture PDFs/DOCX (single column, two-column, tables, header contact, image-only); URL source detection; fetch guard (private IP, redirect to private IP); ranking shortlist formula; analytics bucketing.
- **Backend integration**: real Postgres with pgvector (docker compose / testcontainers), `FakeLLM` returning fixture outputs, `InMemoryQueue`, `LocalBlobStore`. API tests via httpx `AsyncClient` with dev auth; cross-user 404 test for each resource; worker tests for claim idempotency, retry, poison, stuck-task recovery; quota enforcement; crawler upsert/close logic against recorded board API fixtures.
- **Prompt evals** (not in CI): ~10 curated résumé/posting pairs run against Azure OpenAI on demand/nightly; report schema-valid rate, grounding drop rate, no-invention drop rate, score variance across 3 runs.
- **Frontend**: Vitest + React Testing Library + MSW for key components (requirements table, suggestion review, tracker board, task stepper); Playwright e2e against docker compose (dev auth + FakeLLM): upload → analyze → tailor → export → track → recommend → practice.
- **CI** (PR): ruff, mypy, pytest; eslint, tsc, vitest; OpenAPI type generation check; Docker build.

---

## 11. Infrastructure and deployment

**Azure resources (Bicep, `infra/`)**, one resource group `rg-hireready-prod`:
- Log Analytics workspace + Application Insights
- Azure Container Registry (Basic)
- Storage account: blob container `resumes`, queues `tasks` and `tasks-poison`
- PostgreSQL Flexible Server (Burstable B1ms, 32 GB), `vector` extension allow-listed, Entra auth enabled
- Key Vault
- Container Apps environment: `api` (external ingress, min 1 / max 3), `worker` (no ingress, min 0 / max 3, azure-queue scaler), Jobs: `crawler` (cron), `migrate` (manual trigger)
- Static Web App (Free)
- Azure OpenAI account with a chat deployment and an embedding deployment (`text-embedding-3-small`, 1536 dims); deployment names in settings
- User-assigned managed identity with roles: AcrPull, Storage Blob Data Contributor, Storage Queue Data Contributor, Cognitive Services OpenAI User, Key Vault Secrets User; Postgres Entra role
- Budget alert on the resource group

**One-time manual steps (runbook in `docs/runbook.md`)**: create Entra External ID tenant, user flow (Google + email), SPA and API app registrations; request Azure OpenAI model access/quota; set GitHub OIDC federated credential.

**CI/CD (GitHub Actions, OIDC login)** on push to `main`:
1. Run CI.
2. Build backend image tagged with git SHA → push to ACR.
3. Run `migrate` job with the new image; abort on failure.
4. Update `api`, `worker`, `crawler` to the new image.
5. Build and deploy frontend to Static Web Apps (PRs get preview environments).

**Local development**: `docker compose up` (Postgres+pgvector, Azurite, api, worker); `npm run dev` for frontend; `LLM_PROVIDER=fake` or a dev Azure OpenAI endpoint; `AUTH_MODE=dev`.

**v1 retirement**: tag current `main` as `v1-legacy`; remove `ai/`, `resume-analyzer/`, AWS files (`deploy-aws.md`, `trust-policy.json`), Electron, and committed build output; fresh database.

---

## 12. Delivery phases

Each phase gets its own implementation plan, is tested, and is deployed before the next begins.

1. **Foundation**: repo restructure and v1 retirement; backend core (settings, DB, auth, storage, LLM client, task queue + worker, quotas, errors, telemetry); résumé upload + ATS preview; job import; evidence analysis + gaps; frontend shell (auth, home, résumés, jobs, analysis, task stepper, settings); infra + CI/CD; first Azure deployment.
2. **Tailoring**: propose/refine, no-invention check, review UI, DOCX/PDF export, re-analyze.
3. **Tracker**: applications, events, board, analytics; where-should-I-apply ranking.
4. **Recommendations**: companies seed, crawler job, embeddings + pgvector, preferences, `recommend.run`, recommendations UI.
5. **Interview practice**: generate, grade, attempts UI.
