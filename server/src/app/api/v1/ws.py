import io
from datetime import datetime

import aiofiles
import whisper
from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from pydub import AudioSegment

from ...core.config import settings
from ...core.ws_manager import ConnectionManager

router = APIRouter(tags=["ws"])

# Load Whisper Model (Choose from: tiny, base, small, medium, large)
model = whisper.load_model("tiny")
manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    try:
        await manager.connect(websocket, client_id)
        print("Client connected.")

        # Temporary buffer for incoming audio data
        audio_buffer = io.BytesIO()
        print(f"Audio buffer initialized for client {client_id}")

        while True:
            try:
                # Receive message from the client
                message = await websocket.receive()
                print("message", message)

                # Check if the message is a disconnect
                if message.get("type") == "websocket.disconnect":
                    print(
                        f"Disconnect message received for client {client_id}: {message}"
                    )
                    break  # Exit the loop on disconnect

                # # Handle binary audio data (WebM)
                elif message.get("bytes") is not None:
                    audio_data = message.get("bytes")
                    audio_buffer.write(audio_data)

                    # Convert WebM to WAV and save to file
                    audio_buffer.seek(0)
                    webm_audio = AudioSegment.from_file(audio_buffer, format="webm")
                    wav_filepath = f"{settings.MEDIA_DIR}/recording_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                    webm_audio.export(wav_filepath, format="wav")
                    audio_buffer.seek(0)  # Reset buffer after processing

                # else:
                #     print(f"Unknown message type received for client {client_id}: {message}")
            except WebSocketDisconnect:
                print(f"WebSocketDisconnect exception caught for client {client_id}")
                break
            except Exception as inner_e:
                print(f"Inner loop error for client {client_id}: {inner_e}")
    except Exception as e:
        print(f"Outer error in websocket connection for client {client_id}: {e}")
        await websocket.close(code=1000, reason="Server error")
    finally:
        # Cleanup
        await manager.disconnect(client_id)
        print(f"Connection closed for client {client_id}")

    # TODO: send audio file to client and playback
