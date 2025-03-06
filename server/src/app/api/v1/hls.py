# import os
#
# from fastapi import APIRouter, Body, HTTPException, WebSocketDisconnect, WebSocket
# from starlette.responses import FileResponse
#
# from ...core.config import settings
# from ...core.hls_manager import AudioManager
#
# router = APIRouter(tags=["hls"])
#
# manager = AudioManager()
#
# @router.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: str):
#     print(f"WebSocket endpoint called for client_id: {client_id}")
#     try:
#         await manager.connect(websocket, client_id)
#
#         while True:
#             try:
#                 message = await websocket.receive()
#                 print(f"Received message from client {client_id}: {message}")
#
#                 if message.get("type") == "websocket.disconnect":
#                     break
#
#                 if message.get("bytes") is not None:
#                     audio_data = message.get("bytes")
#                     await manager.process_audio_chunk(client_id, audio_data)
#
#             except WebSocketDisconnect:
#                 break
#             except Exception as e:
#                 print(f"Inner loop error for client {client_id}: {e}")
#
#     except Exception as e:
#         print(f"Outer error in websocket connection for client {client_id}: {e}")
#         await websocket.close(code=1000, reason="Server error")
#     finally:
#         await manager.disconnect(client_id)
#         print(f"Connection fully closed for client {client_id}")
#
# @router.get("/stream/{client_id}/playlist.m3u8")
# async def get_hls_playlist(client_id: str):
#     """Serve the HLS playlist."""
#     playlist_path = f"{settings.HLS_MEDIA_DIR}/{client_id}/playlist.m3u8"
#     if not os.path.exists(playlist_path):
#         raise HTTPException(status_code=404, detail="Playlist not found")
#     return FileResponse(playlist_path, media_type="application/vnd.apple.mpegurl")
#
# @router.get("/stream/{client_id}/{segment}")
# async def get_hls_segment(client_id: str, segment: str):
#     """Serve HLS segments."""
#     segment_path = f"{settings.HLS_MEDIA_DIR}/{client_id}/{segment}"
#     if not os.path.exists(segment_path):
#         raise HTTPException(status_code=404, detail="Segment not found")
#     return FileResponse(segment_path, media_type="video/mp2t")
