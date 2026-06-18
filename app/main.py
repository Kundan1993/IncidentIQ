import json
import logging
import os
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.graph import run_triage
from app.rag.retriever import search
from app.schemas import IncidentIn, IncidentReport

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("incidentiq")

app = FastAPI(title="IncidentIQ", version="0.1.0")


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4())[:8])
    start = time.time()
    response = await call_next(request)
    took = round((time.time() - start) * 1000)
    log.info("trace=%s %s %s -> %s (%sms)", trace_id, request.method, request.url.path, response.status_code, took)
    response.headers["x-trace-id"] = trace_id
    return response


@app.get("/health")
def health():
    return {"status": "ok", "mock_llm": get_settings().mock_llm}


@app.post("/process", response_model=IncidentReport)
def process(incident: IncidentIn):
    if not incident.title.strip():
        raise HTTPException(400, "incident title is required")
    return run_triage(incident)


@app.get("/runbooks/{category}")
def get_runbooks(category: str):
    # resource retrieval endpoint - pull knowledge straight from RAG
    hits = search(category, category=category)
    if not hits:
        raise HTTPException(404, f"no knowledge entries for {category}")
    return {"category": category, "entries": hits}


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    # look up a past incident from the corpus by id
    cfg = get_settings()
    if not os.path.exists(cfg.incidents_file):
        raise HTTPException(404, "incident corpus not found")
    with open(cfg.incidents_file, "r", encoding="utf-8") as f:
        incidents = json.load(f)
    for inc in incidents:
        if inc.get("id", "").lower() == incident_id.lower():
            return inc
    raise HTTPException(404, f"incident {incident_id} not found")


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    log.exception("unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "internal error"})
