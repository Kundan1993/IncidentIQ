from app.config import get_settings
from app.rag.store import get_store
from app.schemas import KnowledgeHit


def search(query: str, category: str | None = None) -> list[KnowledgeHit]:
    cfg = get_settings()
    store = get_store()

    flt = {"category": category} if category and category != "other" else None
    results = store.similarity_search_with_score(query, k=cfg.top_k, filter=flt)

    # if the category filter found nothing, retry without it
    if not results and flt is not None:
        results = store.similarity_search_with_score(query, k=cfg.top_k)

    hits = []
    for doc, score in results:
        hits.append(
            KnowledgeHit(
                kind=doc.metadata.get("kind", "runbook"),
                source=doc.metadata.get("source", "unknown"),
                snippet=doc.page_content.strip(),
                score=round(float(score), 4),
            )
        )
    return hits
