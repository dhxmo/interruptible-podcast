import logging
from typing import Dict, Any

from fastapi import WebSocket
from openai import OpenAI


class SpeechGen:

    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:8880/v1", api_key="not-needed")
        self.speaker_lookup = {
            "Host1": "am_puck(1)+am_michael(1.5)",
            "Host2": "am_puck(1)+am_echo(1.5)",
        }

    async def generate_speech(
        self, websocket: WebSocket | None, session: Dict[str, Any], podcast_script: str
    ):
        try:
            lines = [
                line.strip() for line in podcast_script.strip().split("\n") if line
            ]
            dialogues = [
                (line.split(":")[0], line.split(":")[1].strip()) for line in lines
            ]

            for sentence_idx, (speaker, sentence) in enumerate(dialogues):
                if speaker not in self.speaker_lookup:
                    continue

                session["current_sentence_idx"] = sentence_idx

                # TODO: pass websocket and stream OPUS response back to client
                await self.stream_response(
                    websocket, self.speaker_lookup[speaker], sentence
                )
        except Exception as e:
            logging.error(f"error in generating speech: {str(e)}")

    def stream_to_file(self, speaker: str, sentence: str, idx: int):
        with self.client.audio.speech.with_streaming_response.create(
            model="kokoro", voice=speaker, input=sentence
        ) as response:
            response.stream_to_file(f"./data/output_{speaker}_{idx}.mp3")

    async def stream_response(
        self, websocket: WebSocket | None, speaker: str, sentence: str
    ):
        try:
            with self.client.audio.speech.with_streaming_response.create(
                model="kokoro",
                voice=speaker,
                response_format="pcm",  # opus for websocket bytes transfer
                input=sentence,
            ) as response:
                for chunk in response.iter_bytes(chunk_size=1024):
                    await websocket.send_bytes(chunk)
        except Exception as e:
            logging.error(f"error in stream response: {str(e)}")
