import os
import wave

import whisper
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
)
from fastapi import APIRouter

from ...core.setup import sio

router = APIRouter(tags=["wrtc"])


pc = RTCPeerConnection()
model = whisper.load_model("tiny")

# File setup
AUDIO_FILE = "streamed_audio.wav"
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit PCM

# Create/Open WAV file for writing
if os.path.exists(AUDIO_FILE):
    os.remove(AUDIO_FILE)  # Remove old file before starting a new one

wav_file = wave.open(AUDIO_FILE, "wb")
wav_file.setnchannels(CHANNELS)
wav_file.setsampwidth(SAMPLE_WIDTH)
wav_file.setframerate(SAMPLE_RATE)


@sio.on("sdp")
async def process_sdp(data: dict):
    """Handle SDP messages from React Native client"""
    if data["type"] == "offer":
        offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
        await pc.setRemoteDescription(offer)  # Must be set first!

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)  # Set local before sending

        await sio.emit("sdp", {"type": "answer", "sdp": answer.sdp})


@sio.on("ICEcandidate")
async def process_ice(data):
    """Handle ICE candidates"""
    candidate_data = data.get("candidate")
    if candidate_data:
        # Convert dict to RTCIceCandidate object
        candidate = RTCIceCandidate(
            component=1,  # Usually 1 for RTP
            foundation="foundation",  # Placeholder, not required
            priority=0,  # Placeholder, not required
            protocol="udp",  # Extract from candidate_data if needed
            ip=candidate_data["candidate"].split(" ")[4],  # Extract IP
            port=int(candidate_data["candidate"].split(" ")[5]),  # Extract port
            type=candidate_data["candidate"].split(" ")[
                7
            ],  # Extract type (host, srflx, relay)
            sdpMid=candidate_data.get("sdpMid"),
            sdpMLineIndex=candidate_data.get("sdpMLineIndex"),
        )

        await pc.addIceCandidate(candidate)


def save_wav(filename, audio_data, sample_rate=16000):
    """Save raw PCM data as a WAV file"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)


# @pc.on("datachannel")
# def on_datachannel(channel: RTCDataChannel):
#     """Handle WebRTC DataChannel for PCM audio streaming"""
#     print("🎙️ DataChannel opened!")
#
#     @channel.on("message")
#     async def on_message(audio_data):
#         # Append PCM data to WAV file
#         wav_file.writeframes(audio_data)

# TODO: figure out live streaming transcription
# try:
#     pcm_bytes = base64.b64decode(audio_data)
#     int16_data = np.frombuffer(pcm_bytes, dtype=np.int16)  # Convert buffer to int16 array
#     float32_data = int16_data.astype(np.float32) / 32768.0  # Normalize to float32 [-1.0, 1.0]
#
#     # Check if audio contains valid speech
#     if np.abs(float32_data).max() > 0.01:
#         transcription = transcribe_audio(int16_data)
#         print(f"📝 Transcribed Text: {transcription}")
#         # channel.send(transcription)
#     else:
#         print("⚠️ No valid audio detected.")
# except Exception as e:
#     print("❌ Base64 Decoding Error:", e)


# def transcribe_audio(audio_data):
#     """Run Whisper ASR on received Opus audio"""
#     print("🔎 Running Whisper ASR...")
#     result = model.transcribe(audio_data)
#     return result["text"]


# @pc.on("close")
# def on_close():
#     """Close WAV file when WebRTC session ends"""
#     print("🛑 Closing audio file.")
#     wav_file.close()
