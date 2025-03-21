import argparse
import json
import logging
from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

from src.deep_research.search import DeepResearcher
from src.manager import ClientManager
from src.pod_gen.generate import PodGenStandard
from src.tts.speech_gen import SpeechGen
from src.whisper import FasterWhisperEngine

cm = ClientManager()
dr = DeepResearcher()
pg = PodGenStandard()
stt = FasterWhisperEngine()
tts = SpeechGen()

logging.basicConfig(
    level=logging.INFO,  # Set to INFO to see info logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Output to console
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
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
sentenceIndex = 0


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global sentenceIndex, tts

    # make this more robust. add a connection manger
    logger.info("acepting conn")
    await websocket.accept()
    logger.info("accepted")

    session_id = cm.create_session()

    try:
        while True:
            message = await websocket.receive()
            # stt
            if "bytes" in message:
                audio_data = message["bytes"]
                audio_io = BytesIO(audio_data)
                user_query = stt.transcribe_webm(audio_io)

                # find answer against session_id (web results saved against it)
                interruption_answer = await pg.interruption_gen(
                    user_query, cm.sessions[session_id]
                )

                # user interruption is high priority
                await tts.add_priority_request(
                    websocket,
                    action="interruption_tts_response",
                    speaker="Host1",
                    sentence=interruption_answer,
                    idx=0,
                )
            elif "text" in message:
                data = json.loads(message["text"])

                # user prompt parse
                if data.get("action") == "submit_prompt":
                    # conduct research on the web
                    talking_points = await dr.generate_report(
                        data.get("prompt"), cm.sessions[session_id]
                    )
                    # generate podcast based on the running summary and the talking points
                    podcast_script = await pg.podgen(
                        cm.sessions[session_id], talking_points
                    )

                    logger.info("sending podcast script to client", podcast_script)

                    # send script back to client
                    await websocket.send_json(
                        {"action": "convo_transcript", "transcript": podcast_script}
                    )
                # tts
                elif data.get("action") == "tts":
                    host = data.get("host")
                    dialogue = data.get("dialogue")
                    idx = data.get("idx")

                    try:
                        await tts.add_normal_request(
                            websocket,
                            action="tts_response",
                            speaker=host,
                            sentence=dialogue,
                            idx=idx,
                        )
                    except Exception as e:
                        error_response = {"action": "error", "message": str(e)}
                        await websocket.send_json(error_response)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.info("WebSocket endpoint exiting. Cancelling worker.")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=True,
        timeout_keep_alive=120,
        log_level="info",
    )
