"""Mocked DevOps tools the remediation agent can invoke.

Fake on purpose - in real life these would hit Kubernetes / the deploy system /
PagerDuty. They are LangChain tools so an agent can call them, and we also call
them directly from the remediation node for safe actions.
"""
from langchain_core.tools import tool


@tool
def restart_service(service: str) -> dict:
    """Restart a service / deployment. Safe, idempotent action."""
    return {"action": "restart_service", "service": service, "status": "restarted"}


@tool
def scale_replicas(service: str, replicas: int) -> dict:
    """Scale a service to the given number of replicas."""
    return {"action": "scale_replicas", "service": service, "replicas": replicas, "status": "scaled"}


@tool
def rollback_deployment(service: str) -> dict:
    """Roll a service back to its previous deployment."""
    return {"action": "rollback_deployment", "service": service, "status": "rolled_back"}


@tool
def page_oncall(severity: str) -> dict:
    """Page the on-call engineer for high severity incidents."""
    return {"action": "page_oncall", "severity": severity, "status": "paged"}


ALL_TOOLS = [restart_service, scale_replicas, rollback_deployment, page_oncall]

# which tool we'd run for each category (very rough mapping, on purpose)
SAFE_ACTION_BY_CATEGORY = {
    "application": restart_service,
    "infra": scale_replicas,
    "database": restart_service,
    "network": rollback_deployment,
}
