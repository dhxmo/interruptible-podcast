import asyncio
import base64
import io
import logging
from io import BytesIO
from typing import Optional

import requests
from fastapi import WebSocket
from gtts import gTTS
from httplib2.auth import params
from numba.cuda import stream
from openai import OpenAI

from src.config import Config

logging.basicConfig(
    level=logging.INFO,  # Set to INFO to see info logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Output to console
)
logger = logging.getLogger(__name__)


class SpeechGen:
    def __init__(self):
        self.client = OpenAI(
            base_url=Config.kokoro_server_endpoint, api_key="not-needed"
        )
        self.speaker_lookup = {
            # kokoro
            "Host1": "am_puck(1)+am_michael(1.5)",
            "Host2": "am_eric(1)+am_onyx(1.6)",
            # xtts
            # "Host1": "clint",
            # "Host2": "james",
        }
        self.normal_queue = asyncio.Queue()
        self.priority_queue = asyncio.Queue()
        self.processing = False
        self.current_task: Optional[asyncio.Task] = None
        # How long to wait between processing each normal request (in seconds)
        self.normal_processing_delay = 2.0

    async def add_normal_request(self, websocket, action, speaker, sentence, idx):
        logger.info("adding normal request")
        await self.normal_queue.put((websocket, action, speaker, sentence, idx))
        if not self.processing:
            await self.start_processing()

    async def add_priority_request(self, websocket, action, speaker, sentence, idx):
        logger.info("adding priority request")
        await self.priority_queue.put((websocket, action, speaker, sentence, idx))
        if not self.processing:
            await self.start_processing()
        elif self.current_task:
            # If we're already processing something, we don't cancel it
            # but the next item processed will be from the priority queue
            pass

    async def start_processing(self):
        self.processing = True
        self.current_task = asyncio.create_task(self.process_queues())

    async def process_queues(self):
        try:
            while True:
                # Always check priority queue first
                if not self.priority_queue.empty():
                    logger.info("fetching from the priority queue")
                    request = await self.priority_queue.get()
                elif not self.normal_queue.empty():
                    logger.info("fetching from the normal queue")
                    request = await self.normal_queue.get()
                    # Add delay before processing each normal request
                    # This gives time for priority requests to arrive
                    await asyncio.sleep(self.normal_processing_delay)
                else:
                    # Both queues are empty
                    break

                websocket, action, speaker, sentence, idx = request
                await self.stream_response(websocket, action, speaker, sentence, idx)
        except Exception as e:
            logger.error(f"Error processing TTS queue: {str(e)}")
        finally:
            self.processing = False
            self.current_task = None

    def generate_tts_audio(self, speaker: str, sentence: str) -> BytesIO:
        """convert text to audio buffer"""

        logger.info("generating tts audio")

        audio_buffer = io.BytesIO()

        # uncomment for low cpu usage testing
        # tts = gTTS(text=sentence, lang="en")
        # tts.write_to_fp(audio_buffer)
        # audio_buffer.seek(0)

        # kokoro
        with self.client.audio.speech.with_streaming_response.create(
            model="kokoro",
            voice=self.speaker_lookup[speaker],
            response_format="mp3",  # opus for websocket bytes transfer
            input=sentence,
        ) as response:
            for chunk in response.iter_bytes(chunk_size=4096):
                audio_buffer.write(chunk)
            audio_buffer.seek(0)

        # xtts
        # params = {
        #     "text": sentence,
        #     "speaker": self.speaker_lookup[speaker],
        #     "language": "en",
        # }
        # response = requests.get(Config.xtts_server_endpoint, params=params, stream=True)
        # if response.status_code == 200:
        #     for chunk in response.iter_content(chunk_size=1024):
        #         audio_buffer.write(chunk)
        #     audio_buffer.seek(0)
        # else:
        #     logger.error("Error in tts from server")

        return audio_buffer

    async def stream_response(
        self,
        websocket: WebSocket | None,
        action: str,
        speaker: str,
        sentence: str,
        idx: int,
    ):
        try:
            logger.info("handling stream response")
            print("sending for tts", speaker, sentence)

            audio_buffer = self.generate_tts_audio(speaker, sentence)

            # Convert audio buffer to base64
            audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")
            response_data = {
                "action": action,
                "audio": audio_base64,
                "sentenceIndex": idx,
            }

            await websocket.send_json(response_data)
        except Exception as e:
            logger.error(f"error in stream response: {str(e)}")
