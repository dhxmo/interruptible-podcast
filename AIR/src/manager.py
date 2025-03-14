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
            "web_search_results": [],
            "research_loop_count": 0,
            "audio_buffer": b"",
            "conversation": "",
            "llm_output_sentences": deque(),
            "is_processing": False,
        }
        return session_id
