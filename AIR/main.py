import argparse
import base64
import io
import json
from io import BytesIO

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from gtts import gTTS

from tests.constants import podcast_script
from src.deep_research.search import DeepResearcher
from src.pod_gen.generate import PodGenStandard
from src.speech_gen import SpeechGen
from src.whisper import FasterWhisperEngine

dr = DeepResearcher()
pg = PodGenStandard()
stt = FasterWhisperEngine()
tts = SpeechGen()


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
# with open("web/index.html", "r", encoding="utf-8") as f:
#     html = f.read()
#
#
# @app.get("/")
# async def get():
#     return FileResponse("web/index.html")


# @app.websocket("/ws")
# async def ws_endpoint(websocket: WebSocket):
#     global dr, pg, stt, tts
#
#     await websocket.accept()
#     logging.info("connection established")
#
#     try:
#         cm = ClientManager()
#         session_id = cm.create_session()
#
#         while True:
#             message = await websocket.receive()
#             logging.info("received data from client")
#
#             # if bytes received add to input audio buffer
#             if "bytes" in message:
#                 audio_data = message["bytes"]
#                 logging.info(f"received audio data: {len(audio_data)}")
#                 cm.sessions[session_id]["input_audio_buffer"] = audio_data
#             elif "text" in message:
#                 data = json.loads(message["text"])
#
#                 if data["action"] == "submit_prompt":
#                     talking_points = await dr.generate_report(
#                         data["inputPrompt"], cm.sessions[session_id]
#                     )
#
#                     # adds podscript to client manager -> cm.sessions[session_id]["podscript_script"]
#                     await pg.podgen(
#                         cm.sessions[session_id],
#                         talking_points,
#                         data["tone"],
#                     )
#
#                     await tts.generate_speech(
#                         websocket,
#                         cm.sessions[session_id],
#                         cm.sessions[session_id]["podscript_script"],
#                     )
#
#                 elif data["action"] == "init_recording":
#                     print("init recording")
#                     init_text = (
#                         "Host2: oh, I think our human wants to ask something here"
#                     )
#                     # send audio
#                     await tts.generate_speech(
#                         websocket, cm.sessions[session_id], init_text
#                     )
#                     await websocket.send_json({"action": "begin_mic_recording"})
#                 elif data["action"] == "stop_recording":
#                     # transcribe audio data here
#                     print("transcribing data")
#
#             # else process text commands
#     except Exception as e:
#         logging.error(f"error in ws endpoint: {str(e)}")

sentenceIndex = 0


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global sentenceIndex

    await websocket.accept()
    try:
        while True:
            message = await websocket.receive()
            # stt
            if "bytes" in message:
                audio_data = message["bytes"]
                audio_io = BytesIO(audio_data)
                transcription = stt.transcribe_webm(audio_io)

                # generate with last and next sentence -> qwen -> send sentence back to client
                # send interrupt_transcript with audio streaming from the text
                interruption_text = "this is me handling the interruption"
                tts = gTTS(text=interruption_text, lang="en")

                # Save to bytes buffer
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)

                # Send audio bytes back to client
                # await websocket.send_bytes(audio_buffer.read())

                # Convert binary data to base64 for JSON transmission
                audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")

                # Create a structured JSON response
                response = {
                    "action": "tts_response",
                    "sentenceIndex": sentenceIndex,
                    "audio": audio_base64,
                }

                # Send JSON response
                print("sending response")
                await websocket.send_json(response)
            elif "text" in message:
                data = json.loads(message["text"])

                # user prompt parse
                if data.get("action") == "submit_prompt":
                    # generate conversation here

                    # send script back to client
                    await websocket.send_json(
                        {"action": "convo_transcript", "transcript": podcast_script}
                    )
                # tts
                elif data.get("action") == "tts":
                    host = data.get("host")
                    dialogue = data.get("dialogue")
                    sentence_index = data.get("sentenceIndex")
                    sentenceIndex = data.get("sentenceIndex")

                    print("tts init", host, dialogue, sentence_index)

                    try:
                        tts = gTTS(text=dialogue, lang="en")

                        # Save to bytes buffer
                        audio_buffer = io.BytesIO()
                        tts.write_to_fp(audio_buffer)
                        audio_buffer.seek(0)

                        # Send audio bytes back to client
                        # await websocket.end_bytes(audio_buffer.read())

                        # binary audio data
                        audio_bytes = audio_buffer.read()
                        # Convert binary data to base64 for JSON transmission
                        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

                        # Create a structured JSON response
                        response = {
                            "action": "tts_response",
                            "sentenceIndex": sentence_index,
                            "audio": audio_base64,
                        }

                        # Send JSON response
                        print("sending response")
                        await websocket.send_json(response)
                    except Exception as e:
                        error_response = {"action": "error", "message": str(e)}
                        await websocket.send_json(error_response)

                # handle interruption
                elif data.get("action") == "init_interruption":
                    next_sentence = data.get("next_sentence")

                    # generate with qwen response with RAG
                    # flowing the conversation into the next sentence
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level="info",
    )
