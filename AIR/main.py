import argparse
import json

# import logging
import os
import queue
import time

import playsound

# from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from gtts import gTTS

from AIR.playback import (
    generate_audio_files,
    podcast_script,
    play_audio,
    interrupt_queue,
)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     pass


# app = FastAPI(lifespan=lifespan)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------

parser = argparse.ArgumentParser(description="Whisper FastAPI Online Server")
parser.add_argument(
    "--host",
    type=str,
    default="localhost",
    help="The host address to bind the server to.",
)
parser.add_argument(
    "--port", type=int, default=8000, help="The port number to bind the server to."
)
args = parser.parse_args()

# -------------------------

# Load demo HTML for the root endpoint
with open("web/index.html", "r", encoding="utf-8") as f:
    html = f.read()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/asr")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection opened.")

    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = json.loads(data)

            prompt = parsed_data.get("inputPrompt")
            tone = parsed_data.get("tone")

            print(f"Received: Text = {prompt}, Selection = {tone}")

            # generate audio from script
            audio_files = generate_audio_files(podcast_script)

            # # Load Whisper model once
            # model = whisper.load_model("base")
            # sample_rate = 16000
            #
            # # Start listening thread
            # listen_thread = threading.Thread(target=listen_for_stop, args=(model, sample_rate))
            # listen_thread.daemon = True
            # listen_thread.start()

            # Playback loop
            start_line = 0
            while start_line < len(podcast_script):
                # play line
                play_audio(audio_files, start_line=start_line)
                if not interrupt_queue.empty():
                    paused_line = interrupt_queue.get()
                    next_line = (
                        podcast_script[paused_line + 1]
                        if paused_line + 1 < len(podcast_script)
                        else "That’s all for today!"
                    )
                    print("next_line", next_line)

                    # Handle interruption and wait for it to complete
                    # asyncio.run(handle_user_interruption(next_line))

                    # Resume from next line
                    start_line = paused_line + 1
                    if start_line < len(podcast_script):
                        print(f"Resuming from line {start_line + 1}...")
                    else:
                        print("Podcast complete!")
                        break
                else:
                    print("Podcast complete naturally!")
                    break

            # Clean up audio files
            for file in audio_files:
                if os.path.exists(file):
                    os.remove(file)
    except Exception as e:
        print("WebSocket connection closed:", e)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level="info",
    )
