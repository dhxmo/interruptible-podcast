import argparse
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.deep_research.search import DeepResearcher
from src.manager import ClientManager
from src.pod_gen.generate import PodGenStandard
from src.speech_gen import SpeechGen
from src.whisper import FasterWhisperEngine

# dr = DeepResearcher | None
# pg = PodGenStandard | None
# stt = SpeechGen | None
# tts = FasterWhisperEngine | None

dr = DeepResearcher()
pg = PodGenStandard()
stt = FasterWhisperEngine()
tts = SpeechGen()


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     global dr, pg, stt, tts
#
#
#
#     yield
#
#     # free up resources on yield

# app = FastAPI(lifespan=lifespan)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/web", StaticFiles(directory="web"), name="web")

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
    return FileResponse("web/index.html")


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    global dr, pg, stt, tts

    await websocket.accept()
    logging.info("connection established")

    try:
        cm = ClientManager()
        session_id = cm.create_session()

        while True:
            message = await websocket.receive()
            logging.info("received data from client")

            # if bytes received add to input audio buffer
            if "bytes" in message:
                audio_data = message["bytes"]
                logging.info(f"received audio data: {len(audio_data)}")
                cm.sessions[session_id]["input_audio_buffer"] = audio_data
            elif "text" in message:
                data = json.loads(message["text"])
                print(f"data {data}")

                if data["action"] == "submit_prompt":
                    # search -> scrape -> deep-research -> talking_points -> podcast_script_gen -> text to speech
                    pass
                elif data["action"] == "init_recording":
                    print("init recording")
                    init_text = (
                        "Host2: oh, I think our human wants to ask something here"
                    )
                    # send audio
                    await tts.generate_speech(
                        websocket, cm.sessions[session_id], init_text
                    )
                    await websocket.send_json({"action": "begin_mic_recording"})
                elif data["action"] == "stop_recording":
                    # transcribe audio data here
                    print("transcribing data")

            # else process text commands
    except Exception as e:
        logging.error(f"error in ws endpoint: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level="info",
    )
