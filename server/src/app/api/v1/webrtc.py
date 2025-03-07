import whisper
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from fastapi import WebSocket, APIRouter

router = APIRouter(tags=["ws"])


model = whisper.load_model("tiny")
pcs = set()

class AudioProcessor(MediaStreamTrack):
    kind = "audio"

    def __init__(self, track):
        super().__init__()
        self.track = track
        self.audio_buffer = []

    async def recv(self):
        frame = await self.track.recv()
        self.audio_buffer.append(frame.to_ndarray())

        # Process every 500ms of audio
        if len(self.audio_buffer) >= 50:  # Assuming 100fps audio
            audio_data = b"".join(self.audio_buffer)
            with open("temp.wav", "wb") as f:
                f.write(audio_data)
            self.audio_buffer = []

            result = model.transcribe("temp.wav")
            return result["text"]

        return frame  # Pass audio through

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    pcs.add(RTCPeerConnection())

    @pcs[-1].on("track")
    def on_track(track):
        if track.kind == "audio":
            processor = AudioProcessor(track)
            pcs[-1].addTrack(processor)

    while True:
        try:
            data = await websocket.receive_json()
            if "sdp" in data:
                desc = RTCSessionDescription(sdp=data["sdp"], type="offer")
                await pcs[-1].setRemoteDescription(desc)
                answer = await pcs[-1].createAnswer()
                await pcs[-1].setLocalDescription(answer)
                await websocket.send_json({"sdp": pcs[-1].localDescription.sdp})
            elif "candidate" in data:
                await pcs[-1].addIceCandidate(data["candidate"])
        except Exception as e:
            print(f"Error: {e}")
            break

    await pcs[-1].close()
    pcs.remove(pcs[-1])
