from typing import Literal, Optional

from pydantic import BaseModel

Severity = Literal["P1", "P2", "P3", "P4"]
Category = Literal["database", "network", "application", "infra", "other"]


# ---- agent-to-agent contracts ----

class IncidentIn(BaseModel):
    id: Optional[str] = None
    title: str
    description: str = ""


# structured output target for the triage agent
class TriageResult(BaseModel):
    severity: Severity
    category: Category
    entities: list[str] = []
    summary: str


class KnowledgeHit(BaseModel):
    kind: Literal["runbook", "incident"]
    source: str
    snippet: str
    score: float


class RemediationStep(BaseModel):
    action: str
    detail: str


class RemediationPlan(BaseModel):
    steps: list[RemediationStep] = []
    tools_invoked: list[str] = []
    auto_remediated: bool = False


class Notification(BaseModel):
    channel: str
    subject: str
    body: str


class IncidentReport(BaseModel):
    incident_id: str
    severity: Severity
    category: Category
    path: Literal["auto_remediation", "notify_only"]
    triage: TriageResult
    similar: list[KnowledgeHit] = []
    remediation: Optional[RemediationPlan] = None
    notification: Notification
