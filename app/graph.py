r"""LangGraph state machine that wires the agents together.

Flow:
    triage -> knowledge -> (router) -> remediation -> notify
                                   \-> notify

The router is the wow factor: P1/P2 incidents go through the Remediation agent
(which invokes tools), while P3/P4 skip straight to the Notifier.
"""
from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph

from app.agents import knowledge, notifier, remediation, triage
from app.schemas import (
    IncidentIn,
    IncidentReport,
    KnowledgeHit,
    RemediationPlan,
    TriageResult,
)


class TriageState(TypedDict, total=False):
    incident: IncidentIn
    triage: TriageResult
    hits: list[KnowledgeHit]
    remediation: Optional[RemediationPlan]
    report: IncidentReport


def triage_node(state: TriageState) -> TriageState:
    return {"triage": triage.run(state["incident"])}


def knowledge_node(state: TriageState) -> TriageState:
    return {"hits": knowledge.run(state["incident"], state["triage"])}


def remediation_node(state: TriageState) -> TriageState:
    return {"remediation": remediation.run(state["triage"], state["hits"])}


def notify_node(state: TriageState) -> TriageState:
    incident = state["incident"]
    tr = state["triage"]
    rem = state.get("remediation")
    inc_id = incident.id or "INC-AUTO"

    note = notifier.run(inc_id, tr, rem)
    report = IncidentReport(
        incident_id=inc_id,
        severity=tr.severity,
        category=tr.category,
        path="auto_remediation" if rem else "notify_only",
        triage=tr,
        similar=state.get("hits", []),
        remediation=rem,
        notification=note,
    )
    return {"report": report}


def route_by_severity(state: TriageState) -> str:
    # conditional edge - high severity gets auto-remediation, low just gets notified
    if state["triage"].severity in ("P1", "P2"):
        return "remediation"
    return "notify"


def build_graph():
    # node names are kept distinct from the state keys (triage/hits/remediation/...)
    # because LangGraph won't let a node share a name with a state field.
    g = StateGraph(TriageState)
    g.add_node("do_triage", triage_node)
    g.add_node("do_knowledge", knowledge_node)
    g.add_node("do_remediation", remediation_node)
    g.add_node("do_notify", notify_node)

    g.set_entry_point("do_triage")
    g.add_edge("do_triage", "do_knowledge")
    g.add_conditional_edges(
        "do_knowledge",
        route_by_severity,
        {"remediation": "do_remediation", "notify": "do_notify"},
    )
    g.add_edge("do_remediation", "do_notify")
    g.add_edge("do_notify", END)
    return g.compile()


incident_graph = build_graph()


def run_triage(incident: IncidentIn) -> IncidentReport:
    final = incident_graph.invoke({"incident": incident})
    return final["report"]
