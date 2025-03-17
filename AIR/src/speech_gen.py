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
