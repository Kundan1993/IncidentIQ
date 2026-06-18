from langchain_ollama import ChatOllama

from app.config import get_settings


def get_llm():
    cfg = get_settings()
    if cfg.mock_llm:
        from app.mock_llm import FakeChat
        return FakeChat()

    return ChatOllama(
        model=cfg.ollama_model,
        base_url=cfg.ollama_base_url,
        temperature=0,
    )
