import whisper
from aiortc import MediaStreamTrack
from aiortc.contrib.media import MediaRecorder


class AudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, track):
        super().__init__()
        self.track = track
        self.recorder = MediaRecorder("audio.wav")
        self.model = whisper.load_model("tiny")

    async def recv(self):
        frame = await self.track.recv()
        await self.recorder.write_frame(frame)
        return frame

    async def transcribe(self):
        await self.recorder.stop()
        result = self.model.transcribe("audio.wav")
        return result["text"]
