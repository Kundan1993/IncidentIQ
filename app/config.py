from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM stuff
    ollama_model: str = "llama3.1"
    ollama_base_url: str = "http://localhost:11434"
    mock_llm: bool = False

    # rag
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_dir: str = "./chroma_db"
    collection: str = "knowledge"
    top_k: int = 3

    # corpus
    runbooks_dir: str = "./data/runbooks"
    incidents_file: str = "./data/incidents.json"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
