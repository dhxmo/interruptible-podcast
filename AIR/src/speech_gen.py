import asyncio
import base64
import io
import logging
from typing import Dict, Any

from fastapi import WebSocket
from gtts import gTTS
from openai import OpenAI


class SpeechGen:

    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:8880/v1", api_key="not-needed")
        self.speaker_lookup = {
            "Host1": "am_puck(1)+am_michael(1.5)",
            "Host2": "af_bella(1)+af_alloy(1.5)",
        }
        self.normal_queue = asyncio.Queue()
        self.priority_queue = asyncio.Queue()

    async def tts_worker(self, websocket: WebSocket):
        """loop adds to specific queue and processes the job"""
        while True:
            # First check priority queue
            if not self.priority_queue.empty():
                print("getting priorty queue")
                job = await self.priority_queue.get()
            else:
                print("getting normal queue")
                job = await self.normal_queue.get()

            await self.process_tts_job(websocket, job)

    async def add_tts_task(self, action, speaker, sentence, idx):
        job = {
            "action": action,
            "speaker": speaker,
            "sentence": sentence,
            "idx": idx,
        }
        if action == "interruption_tts_response":
            print("adding to priority queue")
            await self.priority_queue.put(job)
        else:
            print("adding to normal queue")
            await self.normal_queue.put(job)

    async def process_tts_job(self, websocket: WebSocket | None, job: Dict[str, str]):
        action = job["action"]
        speaker = job["speaker"]
        sentence = job["sentence"]
        idx = job["idx"]

        print("processing sentence", sentence)

        try:
            audio_buffer = io.BytesIO()

            # for faster local tts
            tts = gTTS(text=sentence, lang="en")
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            # DO NOT DELETE
            # with better compute uncomment this
            # with self.client.audio.speech.with_streaming_response.create(
            #     model="kokoro",
            #     voice=self.speaker_lookup[speaker],
            #     response_format="mp3",  # opus for websocket bytes transfer
            #     input=sentence,
            # ) as response:
            #     for chunk in response.iter_bytes(chunk_size=4096):
            #         # await websocket.send_bytes(chunk)
            #         audio_buffer.write(chunk)
            #     audio_buffer.seek(0)

            # Convert audio to base64
            audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")

            # Create JSON response
            response_data = {
                "action": action,
                "audio": audio_base64,
                "sentenceIndex": idx,
            }

            # Send over WebSocket
            await websocket.send_json(response_data)
        except Exception as e:
            logging.error(f"error in stream response: {str(e)}")
