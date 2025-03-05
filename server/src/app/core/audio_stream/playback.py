import asyncio
import os
import queue
import threading
import time

import numpy as np
import playsound
import sounddevice as sd
import whisper
from gtts import gTTS

from server.src.app.core.genAI.llm import ContentGenerator
from server.src.app.core.genAI.templates import interruption_handle_template

# Static podcast script (5 lines)
podcast_script = [
    "Welcome to today's podcast episode about artificial intelligence.",
    "Today we'll explore how AI is transforming various industries.",
    "From healthcare to transportation, the impact is significant.",
    "Experts predict AI will continue to evolve rapidly in the coming years.",
    "Thanks for listening, stay tuned for more updates next week!",
]

# Global variables
current_line = 0
stop_flag = False
audio_queue = queue.Queue()
interrupt_queue = queue.Queue()  # To signal interruptions and resume points


# -- redundant. Send audio chunks to client
def generate_audio_files(script):
    """Generate audio files for each line and save them"""
    for i, line in enumerate(script):
        tts = gTTS(text=line, lang="en")
        filename = f"line_{i}.mp3"
        tts.save(filename)
    return [f"line_{i}.mp3" for i in range(len(script))]


# -- redundant
def play_audio(audio_files, start_line=0):
    """Play audio files sequentially from a given start line until stopped"""
    global current_line, stop_flag
    for i in range(start_line, len(audio_files)):
        if stop_flag:
            interrupt_queue.put(i)  # Signal interruption with current line
            stop_flag = False  # Reset flag for next interruption
            return  # Exit to wait for interruption handling
        current_line = i
        print(f"Playing line {i + 1}: {podcast_script[i]}")
        playsound.playsound(audio_files[i])
        time.sleep(0.5)  # Small pause between lines


# -- use with websockets
def audio_callback(indata, frames, time_info, status):
    """Callback function for audio input"""
    if status:
        print(f"Audio status: {status}")
    audio_queue.put(indata.copy())


# -- redundant
def listen_for_stop(model, sample_rate):
    """Listen for 'STOP' command using Whisper"""
    global stop_flag
    block_duration = 2  # Record in 2-second chunks

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        callback=audio_callback,
        blocksize=int(sample_rate * block_duration),
    ):
        print("Say 'STOP' to pause the podcast...")
        while True:
            if not audio_queue.empty():
                audio_data = audio_queue.get()
                audio_data = audio_data.flatten().astype(np.float32)
                result = model.transcribe(audio_data, language="en")
                transcribed_text = result["text"].lower()
                print(f"Transcribed: '{transcribed_text}'")
                if "stop" in transcribed_text:
                    stop_flag = True
                    print(f"Paused at line {current_line + 1}")


llm = ContentGenerator()


# make async
async def handle_user_interruption(next_line):
    """Handle user question and generate response"""
    user_input = "will AI take human jobs?"
    next_question = "Today we'll explore how AI is transforming various industries."

    current_context = """
      - **User question**: '{user_input}' 
      - **Next sentence**: '{next_question}' 
    """
    formatted_input = current_context.format(
        user_input=user_input, next_question=next_question
    )

    response = llm.generate_content(formatted_input, interruption_handle_template)
    print("interruption response", response)

    # Convert response to audio
    tts = gTTS(text=response, lang="en")
    response_file = "response.mp3"
    tts.save(response_file)
    playsound.playsound(response_file)
    os.remove(response_file)


def main():
    """
    generate audio file for the script
    have whisper listen for user interaction in thread. if interaction yes. flag it on the global

    while iterating over file in audio_files:
        play the audio files
            if global flagged, note down the current line index in queue

        check queue for index of line that was being spoken just now.
        async -> send next question to llm and generate user query response + fade to next question

        resume playback of audio_files from where it was paused.

    :return:
    """
    # Generate audio files
    audio_files = generate_audio_files(podcast_script)

    # Load Whisper model once
    model = whisper.load_model("base")
    sample_rate = 16000

    # Start listening thread
    listen_thread = threading.Thread(target=listen_for_stop, args=(model, sample_rate))
    listen_thread.daemon = True
    listen_thread.start()

    # Playback loop
    start_line = 0
    while start_line < len(podcast_script):
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
            asyncio.run(handle_user_interruption(next_line))

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


if __name__ == "__main__":
    # Required dependencies: pip install gTTS playsound whisper sounddevice numpy wavio
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
