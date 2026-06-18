"""Tiny fake chat model so tests / CI can run without Ollama.

Set MOCK_LLM=true. It can answer the triage structured-output call (guesses
severity + category from keywords) and returns plain text otherwise.
"""
from app.schemas import TriageResult

_CATEGORY_KEYWORDS = {
    "database": ["db", "database", "postgres", "mysql", "connection pool", "query", "deadlock"],
    "network": ["dns", "network", "timeout", "latency", "packet", "partition", "tls", "certificate"],
    "application": ["500", "exception", "nullpointer", "stacktrace", "api", "endpoint", "memory leak"],
    "infra": ["pod", "node", "disk", "oomkilled", "cpu", "kubernetes", "k8s", "container", "cluster"],
}

# words that usually mean "this is on fire"
_P1_WORDS = ["outage", "down", "data loss", "all users", "p1", "critical", "unavailable"]
_P2_WORDS = ["degraded", "elevated errors", "partial", "slow", "high cpu", "p2"]
_P4_WORDS = ["info", "informational", "notice", "reminder", "low", "p4"]


def _guess_category(text: str) -> str:
    low = text.lower()
    for cat, words in _CATEGORY_KEYWORDS.items():
        if any(w in low for w in words):
            return cat
    return "other"


def _guess_severity(text: str) -> str:
    low = text.lower()
    if any(w in low for w in _P1_WORDS):
        return "P1"
    if any(w in low for w in _P2_WORDS):
        return "P2"
    if any(w in low for w in _P4_WORDS):
        return "P4"
    return "P3"


class _Structured:
    def __init__(self, schema):
        self.schema = schema

    def invoke(self, prompt):
        text = prompt if isinstance(prompt, str) else str(prompt)
        # only look at the actual incident, not the instruction text above it
        # (otherwise we'd match the "P1 (critical/outage)" wording in the prompt)
        if "INCIDENT:" in text:
            text = text.split("INCIDENT:", 1)[1]
        if self.schema.__name__ == "TriageResult":
            return TriageResult(
                severity=_guess_severity(text),
                category=_guess_category(text),
                entities=[],
                summary=text[:120],
            )
        return self.schema()


class FakeChat:
    def with_structured_output(self, schema):
        return _Structured(schema)

    def bind_tools(self, tools):
        return self

    def invoke(self, prompt):
        class _Msg:
            content = (
                "1. Check service health and recent deploys.\n"
                "2. Restart the affected service.\n"
                "3. If unresolved, roll back the last deployment."
            )
        return _Msg()
