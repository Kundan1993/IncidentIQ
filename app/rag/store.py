import os
from functools import lru_cache

# turn off chromadb's posthog telemetry (noisy, not needed)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import get_settings


@lru_cache
def _embeddings():
    cfg = get_settings()
    return HuggingFaceEmbeddings(model_name=cfg.embed_model)


@lru_cache
def get_store() -> Chroma:
    cfg = get_settings()
    return Chroma(
        collection_name=cfg.collection,
        embedding_function=_embeddings(),
        persist_directory=cfg.chroma_dir,
    )
