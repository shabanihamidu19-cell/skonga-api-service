"""
SKONGA Library API — Keyword Search (Phase 1)
===============================================
Uses Postgres tsvector/tsquery for full-text search over topic titles.

Latency notes (Phase 1.1):
  - plainto_tsquery is computed once via CTE (was evaluated twice).
  - content_md is only SELECTed when include_content=True.
  - ILIKE fuzzy fallback runs ONLY when subject_id or form_id is set.
  - Without filters, empty full-text result returns immediately.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session


def _content_select(include_content: bool) -> str:
    return "content_md," if include_content else "NULL::text AS content_md,"


def keyword_search(
    db: Session,
    query: str,
    subject_id: str | None = None,
    form_id: int | None = None,
    top_k: int = 5,
    status_filter: str = "published",
    include_content: bool = True,
) -> list[dict]:
    filters = ["status = :status"]
    params: dict = {"query": query, "status": status_filter, "top_k": top_k}

    if subject_id:
        filters.append("subject_id = :subject_id")
        params["subject_id"] = subject_id

    if form_id:
        filters.append("form_id = :form_id")
        params["form_id"] = form_id

    where_clause = " AND ".join(filters)
    content_col = _content_select(include_content)

    sql = text(f"""
        WITH q AS (
            SELECT plainto_tsquery('simple', :query) AS tsq
        )
        SELECT
            t.id,
            t.subject_id,
            t.form_id,
            t.order_index,
            t.title_en,
            t.title_sw,
            t.difficulty,
            t.status,
            {content_col}
            ts_rank(t.search_vector, q.tsq) AS relevance
        FROM topics t, q
        WHERE {where_clause}
          AND t.search_vector @@ q.tsq
        ORDER BY relevance DESC
        LIMIT :top_k
    """)

    rows = db.execute(sql, params).mappings().all()
    return [dict(row) for row in rows]


def fuzzy_fallback(
    db: Session,
    query: str,
    subject_id: str | None = None,
    form_id: int | None = None,
    top_k: int = 5,
    include_content: bool = True,
) -> list[dict]:
    filters = ["status = 'published'"]
    safe_query = (query or "").strip()[:80]
    params: dict = {"pattern": f"%{safe_query}%", "top_k": top_k}

    if subject_id:
        filters.append("subject_id = :subject_id")
        params["subject_id"] = subject_id
    if form_id:
        filters.append("form_id = :form_id")
        params["form_id"] = form_id

    where_clause = " AND ".join(filters)
    content_col = _content_select(include_content)

    sql = text(f"""
        SELECT
            id, subject_id, form_id, order_index,
            title_en, title_sw, difficulty, status,
            {content_col}
            0.5 AS relevance
        FROM topics
        WHERE {where_clause}
          AND (title_en ILIKE :pattern OR title_sw ILIKE :pattern)
        ORDER BY order_index
        LIMIT :top_k
    """)

    rows = db.execute(sql, params).mappings().all()
    return [dict(row) for row in rows]


def search_topics(
    db: Session,
    query: str,
    subject_id: str | None = None,
    form_id: int | None = None,
    top_k: int = 5,
    include_content: bool = True,
) -> tuple[list[dict], str]:
    results = keyword_search(
        db, query, subject_id, form_id, top_k, include_content=include_content
    )
    if results:
        return results, "fulltext"

    if subject_id or form_id:
        results = fuzzy_fallback(
            db, query, subject_id, form_id, top_k, include_content=include_content
        )
        if results:
            return results, "fuzzy_fallback"

    return [], "fulltext_empty"
