"""Load runbooks + historical incidents into Chroma.

Run once: python -m app.rag.ingest
Persisted to disk so we don't re-ingest on every restart.
"""
import glob
import json
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.rag.store import get_store


def _runbook_docs(folder):
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        out.append((text, os.path.basename(path)))
    return out


def _incident_docs(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        incidents = json.load(f)
    out = []
    for inc in incidents:
        text = (
            f"{inc.get('title', '')}\n{inc.get('description', '')}\n"
            f"Resolution: {inc.get('resolution', '')}"
        )
        out.append((text, inc.get("id", "INC-?"), inc.get("category", "other")))
    return out


def ingest():
    cfg = get_settings()
    store = get_store()
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)

    texts, metas = [], []

    # runbooks (chunked)
    for text, fname in _runbook_docs(cfg.runbooks_dir):
        category = os.path.splitext(fname)[0]
        for chunk in splitter.split_text(text):
            texts.append(chunk)
            metas.append({"kind": "runbook", "source": fname, "category": category})

    # past incidents (one doc each - they're short)
    for text, inc_id, category in _incident_docs(cfg.incidents_file):
        texts.append(text)
        metas.append({"kind": "incident", "source": inc_id, "category": category})

    if not texts:
        print("Nothing to ingest - check data/ folder")
        return

    store.add_texts(texts=texts, metadatas=metas)
    print(f"Ingested {len(texts)} docs (runbooks + incidents)")


if __name__ == "__main__":
    ingest()
