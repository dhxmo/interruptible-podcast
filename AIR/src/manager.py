import uuid
from queue import Queue


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
            "input_audio_buffer": b"",
            "input_user_interruption": "",
            "conversation": "",
            "podscript_script": "",
            "is_processing": False,
            "output_buffer_queue": Queue(maxsize=-1),
        }
        return session_id
