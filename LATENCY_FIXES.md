# RAG Latency Fixes (Phase 1.1)

## What changed

### 1. `app/retrieval/keyword_search.py`
- `plainto_tsquery` evaluated **once** via CTE
- `content_md` only SELECTed when `include_content=True`
- **ILIKE fuzzy fallback only runs when `subject_id` or `form_id` is set**
- New retrieval mode: `fulltext_empty`

### 2. `app/api/v1/rag.py`
- Cache key normalizes query and includes `include_content`
- Stage timings: `cache_ms`, `search_ms`, `build_ms`, `cache_hit`

### 3. `app/api/v1/search.py`
- `include_content` default **False**

### 4. `app/db/migrations/latency_indexes.sql`
- Optional `pg_trgm` + composite indexes

## Production tips
1. Set `REDIS_URL`
2. Run `latency_indexes.sql` on Supabase if needed
3. Pass `subject_hint` / `form_hint` from AI backend
4. Co-locate Render with Supabase region
