import uuid
from collections import deque


class ClientManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "research_topic": "",
            "running_summary": "",
            "follow_up_query": "",
            "web_search_results": [],
            "audio_buffer": b"",
            "conversation": "",
            "llm_output_sentences": deque(),
            "is_processing": False,
        }
        return session_id
