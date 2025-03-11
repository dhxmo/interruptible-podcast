import argparse
import json
import os

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from gtts import gTTS

from AIR.playback import generate_audio_files, podcast_script, stream_audio_file

# from contextlib import asynccontextmanager

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

            if parsed_data.get("type") == "interrupt":
                pass

            prompt = parsed_data.get("inputPrompt")
            tone = parsed_data.get("tone")

            print(f"Received: Text = {prompt}, Selection = {tone}")

            # generate audio from script
            audio_files = generate_audio_files(podcast_script)

            for audio_file in audio_files:
                await websocket.send_text(
                    json.dumps({"type": "start_audio", "filename": audio_file})
                )
                await stream_audio_file(websocket, audio_file)

                if os.path.exists(audio_file):
                    os.remove(audio_file)
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
