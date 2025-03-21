import secrets
import string
from dataclasses import dataclass


def id_generator(length):
    data = string.ascii_uppercase + "0123456789"
    return_str = "".join(secrets.choice(data) for _ in range(length))
    return str(return_str)


@dataclass(kw_only=True)
class Config:
    research_loop_count: int = 1

    # only for testing on local CPU
    # local_llm = "qwen2.5:0.5b"
    # local_llm_reasoning = "qwen2.5:0.5b"
    # local_llm_podcast_gen = "qwen2.5:0.5b"
    # ollama_base_url = "http://localhost:11434/"

    # for testing on remote
    local_llm = "qwen2.5:latest"
    local_llm_reasoning = "deepseek-r1:latest"
    local_llm_podcast_gen = (
        # "hf.co/SentientAGI/Dobby-Mini-Unhinged-Llama-3.1-8B_GGUF:Q8_0"
        "hf.co/NousResearch/Hermes-2-Pro-Llama-3-8B-GGUF:Q8_0"
    )

    search_api = "duckduckgo"
    max_tokens_per_resource = 1000
    search_max_results = 1
    fetch_full_page = True
    ollama_base_url = "http://.../"
    uuid = id_generator(7)
    HF_EMBEDDINGS_MODEL_NAME = "all-MiniLM-L6-v2"
    INDEX_PERSIST_DIRECTORY = "./data/chromadb"

    roles_person1 = (
        "Chaos Gremlin: lights the fuse—spits wild, unhinged takes, yells insane questions, and flips every idea "
        "into a dumpster fire. Hype Beast—screaming, cackling, and cranked to 11 on every damn thing."
    )

    roles_person2 = (
        "Twisted Wingman: rides the crazy train but throws in dark humor, savage jabs, or a warped bro-logic to keep "
        "it rolling. Knows random, gritty shit—drops weird facts or street-smarts like a loose cannon."
    )

    engagement_techniques = (
        "Each host, fueled by their unhinged vibe, hurls a batshit challenge at the audience mid-convo that ties into "
        "the topic or their bro-chaos. They scream it once in the middle to wake listeners up, then blast it again at "
        "the end with a loud, sloppy call-to-action (e.g., ‘Yell at us on X, you cowards!’). The challenges clash their "
        "wild styles—total madness meets gritty hype—for max bro-energy."
    )

    faster_whisper_model = "medium.en"
    # distil-medium.en : 280ms
    # distil-large-v2 : 300 ms
    # distil-large-v3: 300ms
    # large-v2 : 350ms

    xtts_server_endpoint = "http:.../..."
