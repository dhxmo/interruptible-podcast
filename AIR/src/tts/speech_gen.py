import base64
import base64
import io
import logging
from io import BytesIO

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

    @staticmethod
    def generate_tts_audio(speaker: str, sentence: str) -> BytesIO:
        audio_buffer = io.BytesIO()
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
            audio_buffer = self.generate_tts_audio(speaker, sentence)

            # Convert audio bugger to base64
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
