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

    async def stream_response(
        self, websocket: WebSocket | None, speaker: str, sentence: str, idx: int
    ):
        try:
            audio_buffer = io.BytesIO()

            # for faster local tts
            # tts = gTTS(text=sentence, lang="en")
            # tts.write_to_fp(audio_buffer)
            # audio_buffer.seek(0)

            # DO NOT DELETE
            # with better compute uncomment this
            with self.client.audio.speech.with_streaming_response.create(
                model="kokoro",
                voice=self.speaker_lookup[speaker],
                response_format="mp3",  # opus for websocket bytes transfer
                input=sentence,
            ) as response:
                for chunk in response.iter_bytes(chunk_size=4096):
                    # await websocket.send_bytes(chunk)
                    audio_buffer.write(chunk)
                audio_buffer.seek(0)

            # Convert audio to base64
            audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")

            # Create JSON response
            response_data = {
                "action": "tts_response",
                "audio": audio_base64,
                "sentenceIndex": idx,
            }

            # Send over WebSocket
            await websocket.send_json(response_data)
        except Exception as e:
            logging.error(f"error in stream response: {str(e)}")
