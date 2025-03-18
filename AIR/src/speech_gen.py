import logging
from typing import Dict, Any

from fastapi import WebSocket
from openai import OpenAI

# TODO only for local testing purposes
# import pyaudio
#
# player = pyaudio.PyAudio().open(
#     format=pyaudio.paInt16, channels=1, rate=24000, output=True
# )


class SpeechGen:

    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:8880/v1", api_key="not-needed")
        self.speaker_lookup = {
            "Host1": "am_puck(1)+am_michael(1.5)",
            "Host2": "am_puck(1)+am_echo(1.5)",
        }

    async def generate_speech(
        self, websocket: WebSocket, session: Dict[str, Any], podcast_script: str
    ):
        try:
            lines = [
                line.strip() for line in podcast_script.strip().split("\n") if line
            ]
            dialogues = [
                (line.split(":")[0], line.split(":")[1].strip()) for line in lines
            ]

            # add a parallel thread to listen for interruption. process speech ->
            # qwen response based on if sentence_idx-1 , if sentence_idx and if sentence_idx+1
            # initial websocket msg for interruption. generate msg from qwen: "Oh, I think our user wants to ask a question"
            # ... something like this and then stream audio chunks in -> transcribe -> process through qwen
            # (previous sentence spoken + user query + next sentence spoken) -> generate transition sentence between these while
            # contextually answering question

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
