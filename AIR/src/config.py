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

    # only for testing on local CPU
    # local_llm = "qwen2.5:0.5b"
    # local_llm_reasoning = "llama3.2:latest"
    # local_llm_podcast_gen = "llama3.2:latest"

    # for testing on remote
    local_llm = "qwen2.5:latest"  #  test qwen2.5:latest, gemma3:4b and mistral7b
    local_llm_reasoning = "deepseek-r1:latest"
    local_llm_podcast_gen = "deepseek-r1:latest"

    search_api = "duckduckgo"
    max_tokens_per_resource = 1000
    search_max_results = 2
    fetch_full_page = True
    ollama_base_url = "http://localhost:11434/"
    uuid = id_generator(7)
    HF_EMBEDDINGS_MODEL_NAME = "all-MiniLM-L6-v2"
    INDEX_PERSIST_DIRECTORY = "./data/chromadb"

    podcast_name = "AER"
    roles_person1 = "main summarizer"
    roles_person2 = "questioner/clarifier"
    engagement_techniques = "analogies, examples, comparisons, contrast, anecdotes."
    max_num_chunks = 10  # maximum number of rounds of discussions
    min_chunk_size = 200  # minimum number of characters to generate a round of discussion in longform
