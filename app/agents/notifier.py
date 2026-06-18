from app.schemas import Notification, RemediationPlan, TriageResult


def run(incident_id: str, triage: TriageResult, remediation: RemediationPlan | None) -> Notification:
    """Format a Slack/email-ready message. Template-based - no LLM needed here."""
    lines = [
        f"*Incident {incident_id}* — {triage.severity} / {triage.category}",
        f"Summary: {triage.summary}",
    ]
    if remediation and remediation.steps:
        lines.append("\nProposed remediation:")
        for i, s in enumerate(remediation.steps, 1):
            lines.append(f"  {i}. {s.detail}")
        if remediation.tools_invoked:
            lines.append(f"\nActions taken automatically: {', '.join(remediation.tools_invoked)}")
    else:
        lines.append("\nNo automated action taken — logged for awareness.")

    channel = "#sev1-incidents" if triage.severity in ("P1", "P2") else "#ops-fyi"
    return Notification(
        channel=channel,
        subject=f"[{triage.severity}] {triage.summary[:60]}",
        body="\n".join(lines),
    )
