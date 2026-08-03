# SKONGA API Service

Huduma ya ndani ya maarifa ya kielimu (Library / RAG API), inayotumiwa na **SKONGA AI backend pekee**.

> ⚠️ Hii si API ya umma. Client (APK/browser) hairuhusiwi kuwasiliana na API hii moja kwa moja.

Migrated from `skonga-library-api` with **Phase 1.1 RAG latency fixes**.

## Quick start

```bash
cp .env.example .env
# jaza DATABASE_URL + SERVICE_TOKEN_HASH
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints

| Method | Path | Auth |
|--------|------|------|
| GET | `/health` | no |
| GET | `/ready` | no |
| GET | `/internal/v1/subjects` | Bearer |
| GET | `/internal/v1/subjects/{id}` | Bearer |
| GET | `/internal/v1/subjects/{id}/forms/{form}/topics` | Bearer |
| GET | `/internal/v1/topics/{topic_id}` | Bearer |
| POST | `/internal/v1/search` | Bearer |
| POST | `/internal/v1/rag/context` | Bearer |

## Deploy (Render)

- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
- Env: `DATABASE_URL`, `SERVICE_TOKEN_HASH`, `ENVIRONMENT=production`, optional `REDIS_URL`
- Health: `/health`

See `LATENCY_FIXES.md` for RAG performance notes.
