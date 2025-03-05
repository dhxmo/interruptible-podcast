import asyncio
import queue

import numpy as np
import sounddevice as sd
import whisper


class PodcastSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.current_line = 0
        self.stop_flag = False
        self.audio_queue = queue.Queue()
        self.podcast_script = ["Line 1", "Line 2", "Line 3"]
        self.audio_files = [f"line_{i}.mp3" for i in range(len(self.podcast_script))]


async def play_audio(session):
    while session.current_line < len(session.podcast_script):
        if session.stop_flag:
            return
        print(f"User {session.user_id} - Playing line {session.current_line + 1}")
        await asyncio.sleep(0.5)  # Simulate async playback
        session.current_line += 1


async def listen_for_stop(session, model, sample_rate):
    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        callback=lambda indata, frames, t, s: session.audio_queue.put(indata.copy()),
    ):
        while True:
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None, session.audio_queue.get
            )
            result = model.transcribe(audio_data.flatten().astype(np.float32))
            if "stop" in result["text"].lower():
                session.stop_flag = True
                await handle_user_interruption(session)


async def handle_user_interruption(session):
    next_line = (
        session.podcast_script[session.current_line + 1]
        if session.current_line + 1 < len(session.podcast_script)
        else "End"
    )
    print(f"User {session.user_id} - Handling interruption, next: {next_line}")
    await asyncio.sleep(2)  # Simulate response playback
    session.stop_flag = False


async def main():
    model = whisper.load_model("base")
    sample_rate = 16000
    sessions = {"user1": PodcastSession("user1"), "user2": PodcastSession("user2")}

    tasks = []
    for user_id, session in sessions.items():
        tasks.append(play_audio(session))
        tasks.append(listen_for_stop(session, model, sample_rate))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
