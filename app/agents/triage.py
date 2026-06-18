from app.llm import get_llm
from app.schemas import IncidentIn, TriageResult

_PROMPT = (
    "You are an SRE triage assistant. Read the incident and classify it.\n"
    "- severity: P1 (critical/outage), P2 (major/degraded), P3 (minor), P4 (informational)\n"
    "- category: database, network, application, infra, or other\n"
    "- entities: service names, hostnames, error codes you can spot\n"
    "- summary: one line\n\n"
    "INCIDENT:\nTitle: {title}\nDescription: {desc}\n"
)


def run(incident: IncidentIn) -> TriageResult:
    triager = get_llm().with_structured_output(TriageResult)
    try:
        return triager.invoke(_PROMPT.format(title=incident.title, desc=incident.description))
    except Exception:
        # never let triage crash the pipeline - default to a middle severity
        return TriageResult(
            severity="P3",
            category="other",
            entities=[],
            summary=incident.title[:120],
        )
