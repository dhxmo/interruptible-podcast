# import asyncio
# import io
# import os
#
# from fastapi import HTTPException, WebSocket
# from pydub import AudioSegment
# import ffmpeg
#
# from .config import settings
# from ..utils.logger import logger
#
# # Constants
# SAMPLE_RATE = 44100
# CHANNELS = 1
# SEGMENT_DURATION = 2  # Seconds per segment
#
# class AudioManager:
#     def __init__(self):
#         self.active_connections = {}
#         self.audio_queues = {}
#         self.ffmpeg_processes = {}
#
#     async def connect(self, websocket: WebSocket, client_id: str):
#         await websocket.accept()
#         self.active_connections[client_id] = websocket
#         self.audio_queues[client_id] = asyncio.Queue()
#         await self.start_ffmpeg_stream(client_id)
#         print(f"Client {client_id} connected and FFmpeg stream started")
#
#     async def disconnect(self, client_id: str):
#         if client_id in self.active_connections:
#             del self.active_connections[client_id]
#         if client_id in self.audio_queues:
#             del self.audio_queues[client_id]
#         if client_id in self.ffmpeg_processes:
#             process = self.ffmpeg_processes.pop(client_id)
#             process.terminate()
#             print(f"FFmpeg process terminated for {client_id}")
#         print(f"Client {client_id} disconnected")
#
#     async def start_ffmpeg_stream(self, client_id: str):
#         """Start FFmpeg to generate live HLS stream."""
#         output_dir = f"{settings.HLS_MEDIA_DIR}/{client_id}"
#         playlist_path = f"{output_dir}/playlist.m3u8"
#         os.makedirs(output_dir, exist_ok=True)
#
#         try:
#             # FFmpeg process with pipe input for live streaming
#             process = (
#                 ffmpeg
#                 .input('pipe:', format='wav')
#                 .output(
#                     playlist_path,
#                     format='hls',
#                     hls_time=SEGMENT_DURATION,
#                     hls_list_size=5,  # Keep last 5 segments in playlist
#                     hls_flags='delete_segments',  # Remove old segments
#                     hls_segment_type='mpegts',
#                 )
#                 .overwrite_output()
#                 .run_async(pipe_stdin=True)
#             )
#             self.ffmpeg_processes[client_id] = process
#             print(f"Started FFmpeg live stream for {client_id}")
#         except ffmpeg.Error as e:
#             logger.error(f"FFmpeg setup error for {client_id}: {e}")
#             raise
#
#     async def process_audio_chunk(self, client_id: str, audio_data: bytes):
#         """Process WebM chunk and feed to FFmpeg."""
#         queue = self.audio_queues.get(client_id)
#         if not queue or client_id not in self.ffmpeg_processes:
#             print(f"No queue or FFmpeg process for {client_id}")
#             return
#
#         # Convert WebM chunk to WAV
#         try:
#             webm_audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
#             wav_io = io.BytesIO()
#             webm_audio.export(wav_io, format="wav")
#             wav_bytes = wav_io.getvalue()
#             print(f"Converted WebM chunk to WAV for {client_id}, size: {len(wav_bytes)} bytes")
#
#             # Feed WAV bytes to FFmpeg pipe
#             process = self.ffmpeg_processes[client_id]
#             process.stdin.write(wav_bytes)
#             print(f"Fed WAV chunk to FFmpeg for {client_id}")
#         except Exception as e:
#             logger.error(f"Error processing audio chunk for {client_id}: {e}")
