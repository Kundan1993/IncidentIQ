from app.llm import get_llm
from app.schemas import KnowledgeHit, RemediationPlan, RemediationStep, TriageResult
from app.tools.mock_tools import SAFE_ACTION_BY_CATEGORY, page_oncall

_PROMPT = (
    "You are an SRE remediation assistant. Based on the incident and the matching "
    "runbooks / past incidents below, list 3-5 concrete remediation steps. "
    "Be specific and reference the runbook where relevant.\n\n"
    "SEVERITY: {severity}  CATEGORY: {category}\n"
    "SUMMARY: {summary}\n\n"
    "KNOWLEDGE:\n{knowledge}\n"
)


def _parse_steps(text: str) -> list[RemediationStep]:
    steps = []
    for line in text.splitlines():
        line = line.strip().lstrip("0123456789.-) ").strip()
        if line:
            steps.append(RemediationStep(action=line[:60], detail=line))
    return steps[:5] or [RemediationStep(action="manual review", detail="No automated steps generated.")]


def run(triage: TriageResult, hits: list[KnowledgeHit]) -> RemediationPlan:
    llm = get_llm()
    knowledge = "\n---\n".join(h.snippet for h in hits) or "(no matching runbooks)"

    try:
        resp = llm.invoke(
            _PROMPT.format(
                severity=triage.severity,
                category=triage.category,
                summary=triage.summary,
                knowledge=knowledge,
            )
        )
        steps = _parse_steps(resp.content)
    except Exception:
        steps = [RemediationStep(action="manual review", detail="LLM unavailable.")]

    tools_invoked = []

    # P1/P2 always pages on-call
    if triage.severity in ("P1", "P2"):
        page_oncall.invoke({"severity": triage.severity})
        tools_invoked.append("page_oncall")

    # invoke the safe action mapped to this category
    action = SAFE_ACTION_BY_CATEGORY.get(triage.category)
    if action is not None:
        if action.name == "scale_replicas":
            action.invoke({"service": "affected-service", "replicas": 3})
        else:
            action.invoke({"service": "affected-service"})
        tools_invoked.append(action.name)

    return RemediationPlan(steps=steps, tools_invoked=tools_invoked, auto_remediated=bool(tools_invoked))
