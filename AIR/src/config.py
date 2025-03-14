import secrets
import string
from dataclasses import dataclass


def id_generator(length):
    data = string.ascii_uppercase + "0123456789"
    return_str = "".join(secrets.choice(data) for _ in range(length))
    return str(return_str)


@dataclass(kw_only=True)
class Config:
    research_loop_count: int = 3
    local_llm = "qwen2.5:latest"
    # local_llm = "deepseek-r1:8b"
    search_api = "duckduckgo"
    max_tokens_per_resource = 1000
    search_max_results = 1
    fetch_full_page = True
    ollama_base_url = "http://localhost:11434/"
    uuid = id_generator(7)
    HF_EMBEDDINGS_MODEL_NAME = "all-MiniLM-L6-v2"
    INDEX_PERSIST_DIRECTORY = "./data/chromadb"
