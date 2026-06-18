"""Optional: (re)generate the historical incidents corpus with an LLM.

The repo already ships a working corpus under data/, so this is optional.
Run it for a fresh/larger set:

    python generate_data.py

Uses the same Ollama model the app uses. Writes data/incidents.json.
Runbooks are hand-maintained under data/runbooks (we don't regenerate those).
"""
import json
import os
import re

from langchain_ollama import ChatOllama

from app.config import get_settings

PROMPT = """Generate 25 realistic production incidents as a JSON array. Each object must have:
- id (string, format INC-XXX)
- title (short, like a real alert)
- description (2-3 sentences, includes error messages and metrics)
- severity (P1/P2/P3/P4)
- category (database, network, application, infra)
- resolution (the actual fix that worked)
- resolved_at (ISO timestamp in 2025)
Cover varied scenarios: DB connection pools, OOMKilled pods, disk full, Redis high CPU,
DNS failures, certificate expiry, slow queries, rate limits, deployment rollbacks, network partitions.
Output JSON only, no markdown fences."""


def main():
    cfg = get_settings()
    llm = ChatOllama(model=cfg.ollama_model, base_url=cfg.ollama_base_url, temperature=0.4)

    raw = llm.invoke(PROMPT).content
    # models sometimes wrap output in ```json ... ``` - strip that
    raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    try:
        incidents = json.loads(raw)
    except json.JSONDecodeError:
        print("Model did not return valid JSON. Raw output:\n", raw[:500])
        return

    os.makedirs(os.path.dirname(cfg.incidents_file), exist_ok=True)
    with open(cfg.incidents_file, "w", encoding="utf-8") as f:
        json.dump(incidents, f, indent=2)

    print(f"Wrote {len(incidents)} incidents to {cfg.incidents_file}")
    print("now run: python -m app.rag.ingest")


if __name__ == "__main__":
    main()
