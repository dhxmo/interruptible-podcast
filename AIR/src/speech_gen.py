from typing import Dict, Any

from fastapi import WebSocket
from openai import OpenAI

# TODO only for local testing purposes
import pyaudio

player = pyaudio.PyAudio().open(
    format=pyaudio.paInt16, channels=1, rate=24000, output=True
)


class SpeechGen:

    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:8880/v1", api_key="not-needed")
        self.speaker_lookup = {
            "Host1": "am_puck(1)+am_michael(1.5)",
            "Host2": "am_puck(1)+am_echo(1.5)",
        }

    def generate_speech(self, session: Dict[str, Any], podcast_script: str):
        lines = [line.strip() for line in podcast_script.strip().split("\n") if line]
        dialogues = [(line.split(":")[0], line.split(":")[1].strip()) for line in lines]

        # add a parallel thread to listen for interruption. process speech ->
        # qwen response based on if sentence_idx-1 , if sentence_idx and if sentence_idx+1

        for sentence_idx, (speaker, sentence) in enumerate(dialogues):
            if speaker not in self.speaker_lookup:
                continue

            session["current_sentence_idx"] = sentence_idx

            # TODO: pass websocket and stream OPUS response back to client
            self.stream_response(None, self.speaker_lookup[speaker], sentence)

    def stream_to_file(self, speaker: str, sentence: str, idx: int):
        with self.client.audio.speech.with_streaming_response.create(
            model="kokoro", voice=speaker, input=sentence
        ) as response:
            response.stream_to_file(f"./data/output_{speaker}_{idx}.mp3")

    def stream_response(self, websocket: WebSocket | None, speaker: str, sentence: str):
        with self.client.audio.speech.with_streaming_response.create(
            model="kokoro",
            voice=speaker,
            response_format="pcm",  # opus for websocket bytes transfer
            input=sentence,
        ) as response:
            for chunk in response.iter_bytes(chunk_size=1024):
                player.write(chunk)  # TODO: testing only
                # await websocket.send_bytes(chunk)
