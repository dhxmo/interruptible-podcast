import logging
from typing import BinaryIO, Dict, Any

from faster_whisper import WhisperModel
import torch
from numpy import ndarray

from AIR.src.config import Config


class FasterWhisperEngine:
    def __init__(self):
        model_size = Config.faster_whisper_model
        self.model = WhisperModel(
            model_size,
            device="cuda" if torch.cuda.is_available() else "cpu",
            compute_type="float16" if torch.cuda.is_available() else "int8",
        )

    # TODO prod: stream transcribe instead of from file
    def transcribe(self, session: Dict[str, Any], audio: str | BinaryIO | ndarray):
        segments, _ = self.model.transcribe(audio, beam_size=5)
        full_text = "".join(segment.text for segment in segments)
        logging.info(f"transcribed text: {full_text}")

        session["input_user_interruption"] = full_text

        return full_text
