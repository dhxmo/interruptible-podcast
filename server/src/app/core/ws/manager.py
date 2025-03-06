import asyncio
import base64
import json
import queue
from datetime import datetime
from typing import Dict

import sounddevice as sd
import soundfile as sf
from fastapi import WebSocket

from server.src.app.utils.logger import logger


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.audio_streams: Dict[str, sd.InputStream] = {}
        self.audio_queues: Dict[str, queue.Queue] = {}
        self.output_streams: Dict[str, sd.OutputStream] = {}
        self.audio_files: Dict[str, sf.SoundFile] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> bool:
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.audio_queues[client_id] = queue.Queue()

            SAMPLE_RATE = 44100
            CHANNELS = 2
            BLOCK_SIZE = 1024

            def audio_callback(indata, frames, time, status):
                if status:
                    logger.error(f"Audio callback status: {status}")
                self.audio_queues[client_id].put(indata.copy())

            # Input stream
            input_stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=BLOCK_SIZE,
                callback=audio_callback,
            )
            input_stream.start()
            self.audio_streams[client_id] = input_stream

            # Output stream
            # output_stream = sd.OutputStream(
            #     samplerate=SAMPLE_RATE,
            #     channels=CHANNELS,
            #     blocksize=BLOCK_SIZE
            # )
            # output_stream.start()
            # self.output_streams[client_id] = output_stream

            # Audio file setup
            filename = (
                f"recording_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            )
            audio_file = sf.SoundFile(
                filename,
                mode="w",
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                format="WAV",
            )
            self.audio_files[client_id] = audio_file

            logger.info(f"Client {client_id} connected, recording to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error connecting client {client_id}: {e}")
            return False

    async def disconnect(self, client_id: str):
        try:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            if client_id in self.audio_streams:
                self.audio_streams[client_id].stop()
                self.audio_streams[client_id].close()
                del self.audio_streams[client_id]
            if client_id in self.output_streams:
                self.output_streams[client_id].stop()
                self.output_streams[client_id].close()
                del self.output_streams[client_id]
            if client_id in self.audio_queues:
                del self.audio_queues[client_id]
            if client_id in self.audio_files:
                self.audio_files[client_id].close()
                del self.audio_files[client_id]
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting client {client_id}: {e}")

    async def send_audio_chunk(self, audio_data: bytes, client_id: str):
        if client_id in self.active_connections:
            try:
                audio_encoded = base64.b64encode(audio_data).decode("utf-8")
                await self.active_connections[client_id].send_text(
                    json.dumps(
                        {
                            "type": "audio",
                            "data": audio_encoded,
                            "sample_rate": 44100,
                            "channels": 2,
                        }
                    )
                )
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                await self.disconnect(client_id)

    async def process_and_stream(self, client_id: str):
        audio_queue = self.audio_queues.get(client_id)
        output_stream = self.output_streams.get(client_id)
        audio_file = self.audio_files.get(client_id)

        while client_id in self.active_connections:
            try:
                if audio_queue and not audio_queue.empty():
                    audio_chunk = audio_queue.get_nowait()
                    processed_chunk = audio_chunk  # Add processing here if needed

                    # Save to file
                    if audio_file:
                        audio_file.write(processed_chunk)

                    # Send to client
                    await self.send_audio_chunk(processed_chunk.tobytes(), client_id)

                    # Play locally (optional)
                    if output_stream:
                        output_stream.write(processed_chunk)
            except queue.Empty:
                await asyncio.sleep(0.01)
            except Exception as e:
                logger.error(f"Error processing audio for {client_id}: {e}")
                break
