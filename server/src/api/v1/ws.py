import asyncio
import base64
import json

import numpy as np
from fastapi import WebSocket, WebSocketDisconnect, APIRouter

from server.src.app.core.ws.manager import ConnectionManager
from server.src.app.utils.logger import logger

router = APIRouter(tags=["ws"])
manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    if not await manager.connect(websocket, client_id):
        return

    processing_task = asyncio.create_task(manager.process_and_stream(client_id))

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "audio_chunk":
                audio_bytes = base64.b64decode(message["data"])
                audio_array = np.frombuffer(audio_bytes, dtype=np.float32)

                processed_audio = audio_array  # Add processing here if needed

                # Save to file
                if client_id in manager.audio_files:
                    manager.audio_files[client_id].write(processed_audio)

                # Send processed audio back
                await manager.send_audio_chunk(processed_audio.tobytes(), client_id)

                # Play locally (optional)
                # if client_id in manager.output_streams:
                #     manager.output_streams[client_id].write(processed_audio)

    except WebSocketDisconnect:
        processing_task.cancel()
        await manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Error in WebSocket {client_id}: {e}")
        processing_task.cancel()
        await manager.disconnect(client_id)
