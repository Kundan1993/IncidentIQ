from app.rag.retriever import search
from app.schemas import IncidentIn, KnowledgeHit, TriageResult


def run(incident: IncidentIn, triage: TriageResult) -> list[KnowledgeHit]:
    """RAG lookup over runbooks + past incidents for this incident."""
    query = f"{incident.title}. {incident.description} {triage.summary}".strip()
    return search(query, category=triage.category)
