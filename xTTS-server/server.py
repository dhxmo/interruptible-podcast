import io
import logging

import soundfile as sf
import torch
import uvicorn
from TTS.api import TTS
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

# Define the FastAPI app
app = FastAPI(title="Text-to-Speech API")

speaker_lookup = {"clint": "voices/clint.wav", "james": "voices/james.wav"}


# TTS class to handle model loading and inference
class TTSEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
        print("TTS model loaded and setup complete...")

    def generate_audio(self, text: str, speaker: str, language: str) -> io.BytesIO:
        # Generate the waveform
        wav = self.tts.tts(
            text=text, speaker_wav=speaker_lookup[speaker], language=language
        )
        if isinstance(wav, torch.Tensor):
            wav = wav.numpy()

        # Write the numpy array to an in-memory buffer in WAV format
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, wav, samplerate=22050, format="WAV")
        audio_buffer.seek(0)
        return audio_buffer


# Instantiate the TTS engine globally (loaded once at startup)
tts_engine = TTSEngine()


# Define the GET endpoint with query parameters
@app.get("/generate-audio/")
async def generate_audio(
    text: str = Query(..., description="Text to convert to speech"),
    speaker: str = Query(..., description="Path to speaker WAV file"),
    language: str = Query("en", description="Language code (e.g., 'en')"),
):
    try:
        # Generate the audio buffer
        audio_buffer = tts_engine.generate_audio(text, speaker, language)

        # Stream the audio data
        return StreamingResponse(
            audio_buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=output.wav"},
        )
    except Exception as e:
        logging.error(f"error in generating speech: {str(e)}")


# Run the server with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
