import asyncio
import os
from gtts import gTTS
import sounddevice as sd
import numpy as np
import whisper
import logging
from arq import create_pool
from arq.connections import RedisSettings
from arq.cron import cron
from typing import Dict, List
import redis.asyncio as redis

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Static podcast script
PODCAST_SCRIPT = [
    "Welcome to today's podcast episode about artificial intelligence.",
    "Today we'll explore how AI is transforming various industries.",
    "From healthcare to transportation, the impact is significant.",
    "Experts predict AI will continue to evolve rapidly in the coming years.",
    "Thanks for listening, stay tuned for more updates next week!",
]

# Redis settings
REDIS_SETTINGS = RedisSettings(host="localhost", port=6379, database=0)


# Placeholder ContentGenerator (replace with actual LLM)
class ContentGenerator:
    async def generate_content(self, formatted_input: str, template: str) -> str:
        await asyncio.sleep(0.1)  # Simulate async LLM call
        return (
            f"Here's an answer to '{formatted_input}': AI might shift jobs. {template}"
        )


class PodcastSession:
    def __init__(self, user_id: str, redis_pool):
        self.user_id = user_id
        self.redis_pool = redis_pool
        self.audio_files = self._generate_audio_files()
        self.running = True

    async def get_current_line(self) -> int:
        """Get current line from Redis."""
        line = await self.redis_pool.get(f"{self.user_id}:current_line")
        return int(line) if line else 0

    async def set_current_line(self, line: int):
        """Set current line in Redis."""
        await self.redis_pool.set(f"{self.user_id}:current_line", line)

    def _generate_audio_files(self) -> List[str]:
        """Generate audio files for the podcast script."""
        files = []
        try:
            for i, line in enumerate(PODCAST_SCRIPT):
                tts = gTTS(text=line, lang="en")
                filename = f"{self.user_id}_line_{i}.mp3"
                tts.save(filename)
                files.append(filename)
        except Exception as e:
            logger.error(f"Failed to generate audio files for {self.user_id}: {e}")
            raise
        return files

    def cleanup(self):
        """Clean up audio files."""
        for file in self.audio_files:
            if os.path.exists(file):
                os.remove(file)


# ARQ worker functions
async def play_audio(ctx, user_id: str, line: int):
    """ARQ task to play a single line of audio."""
    redis_pool = ctx["redis"]
    session = PodcastSession(user_id, redis_pool)
    try:
        if line < len(PODCAST_SCRIPT):
            logger.info(
                f"User {user_id} - Playing line {line + 1}: {PODCAST_SCRIPT[line]}"
            )
            # Simulate async audio playback (replace with real async audio)
            await asyncio.sleep(
                2
            )  # Placeholder for playsound.playsound(session.audio_files[line])
            await session.set_current_line(line + 1)
            # Queue next line if not interrupted
            if await redis_pool.get(f"{user_id}:interrupted") != b"1":
                await ctx["redis"].enqueue_job("play_audio", user_id, line + 1)
    except Exception as e:
        logger.error(f"User {user_id} - Playback error at line {line + 1}: {e}")
    finally:
        session.cleanup()


async def handle_user_interruption(ctx, user_id: str, line: int):
    """ARQ task to handle user interruption."""
    redis_pool = ctx["redis"]
    session = PodcastSession(user_id, redis_pool)
    try:
        next_line = (
            PODCAST_SCRIPT[line + 1]
            if line + 1 < len(PODCAST_SCRIPT)
            else "That’s all for today!"
        )
        user_input = "will AI take human jobs?"  # Replace with dynamic input if needed

        current_context = """
          - **User question**: '{user_input}' 
          - **Next sentence**: '{next_line}' 
        """
        formatted_input = current_context.format(
            user_input=user_input, next_line=next_line
        )

        llm = ContentGenerator()
        response = await llm.generate_content(formatted_input, next_line)
        logger.info(f"User {user_id} - Responding: {response}")

        # Generate and play response audio
        tts = gTTS(text=response, lang="en")
        response_file = f"{user_id}_response.mp3"
        tts.save(response_file)
        await asyncio.sleep(2)  # Placeholder for playsound.playsound(response_file)
        os.remove(response_file)

        # Reset interruption flag and resume playback
        await redis_pool.set(f"{user_id}:interrupted", 0)
        await session.set_current_line(line + 1)
        await ctx["redis"].enqueue_job("play_audio", user_id, line + 1)
    except Exception as e:
        logger.error(f"User {user_id} - Interruption handling error: {e}")
        await redis_pool.set(f"{user_id}:interrupted", 0)  # Reset to avoid stalling
    finally:
        session.cleanup()


def audio_callback(indata, frames, time_info, status, audio_queue: asyncio.Queue):
    """Callback function for audio input."""
    if status:
        logger.warning(f"Audio status: {status}")
    try:
        audio_queue.put_nowait(indata.copy())
    except asyncio.QueueFull:
        logger.warning("Audio queue full, dropping data")


async def listen_for_stop(
    user_id: str, model: whisper.Whisper, sample_rate: int, redis_pool
):
    """Listen for 'STOP' command and enqueue interruption."""
    audio_queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            callback=lambda indata, frames, t, s: audio_callback(
                indata, frames, t, s, audio_queue
            ),
            blocksize=int(sample_rate * 2),
        ):  # 2-second chunks
            logger.info(f"User {user_id} - Listening for 'STOP'...")
            while True:
                try:
                    audio_data = await audio_queue.get()
                    audio_data = audio_data.flatten().astype(np.float32)
                    result = await loop.run_in_executor(
                        None, model.transcribe, audio_data, {"language": "en"}
                    )
                    transcribed_text = result["text"].lower()
                    logger.debug(f"User {user_id} - Transcribed: '{transcribed_text}'")

                    if "stop" in transcribed_text:
                        current_line = await PodcastSession(
                            user_id, redis_pool
                        ).get_current_line()
                        logger.info(
                            f"User {user_id} - Detected 'STOP' at line {current_line + 1}"
                        )
                        await redis_pool.set(f"{user_id}:interrupted", 1)
                        await redis_pool.enqueue_job(
                            "handle_user_interruption", user_id, current_line
                        )
                except Exception as e:
                    logger.error(f"User {user_id} - Whisper processing error: {e}")
                    await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"User {user_id} - Audio stream error: {e}")


# ARQ worker setup
async def startup(ctx):
    """Startup hook for ARQ worker."""
    logger.info("ARQ worker starting...")


async def shutdown(ctx):
    """Shutdown hook for ARQ worker."""
    logger.info("ARQ worker shutting down...")


class WorkerSettings:
    functions = [play_audio, handle_user_interruption]
    redis_settings = REDIS_SETTINGS
    on_startup = startup
    on_shutdown = shutdown


async def run_session(
    user_id: str, model: whisper.Whisper, sample_rate: int, redis_pool
):
    """Run a podcast session for a single user."""
    await redis_pool.set(f"{user_id}:interrupted", 0)
    await redis_pool.set(f"{user_id}:current_line", 0)
    await redis_pool.enqueue_job("play_audio", user_id, 0)
    await listen_for_stop(user_id, model, sample_rate, redis_pool)


async def main():
    """Main entry point to manage multiple user sessions."""
    model = whisper.load_model("base")
    sample_rate = 16000
    redis_pool = await create_pool(REDIS_SETTINGS)

    user_sessions = ["user1", "user2"]
    tasks = [
        run_session(user_id, model, sample_rate, redis_pool)
        for user_id in user_sessions
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Main loop cancelled")
    except Exception as e:
        logger.error(f"Main loop error: {e}")
    finally:
        redis_pool.close()
        await redis_pool.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
