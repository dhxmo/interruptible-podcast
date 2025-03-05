from gtts import gTTS
import os
import time
import playsound
import whisper
import sounddevice as sd
import numpy as np
import threading
import queue
import wavio

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


def generate_audio_files(script):
    """Generate audio files for each line and save them"""
    for i, line in enumerate(script):
        tts = gTTS(text=line, lang="en")
        filename = f"line_{i}.mp3"
        tts.save(filename)
    return [f"line_{i}.mp3" for i in range(len(script))]


def play_audio(audio_files):
    """Play audio files sequentially until stopped"""
    global current_line, stop_flag
    for i in range(len(audio_files)):
        if stop_flag:
            break
        current_line = i
        print(f"Playing line {i + 1}: {podcast_script[i]}")
        playsound.playsound(audio_files[i])
        time.sleep(0.5)  # Small pause between lines
    stop_flag = False  # Reset flag after completion


def audio_callback(indata, frames, time_info, status):
    """Callback function for audio input"""
    if status:
        print(f"Audio status: {status}")
    audio_queue.put(indata.copy())


def listen_for_stop():
    """Listen for 'STOP' command using Whisper"""
    global stop_flag
    model = whisper.load_model("base")
    sample_rate = 16000
    block_duration = 2  # Record in 2-second chunks

    print("Available audio devices:")
    print(sd.query_devices())

    try:
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
                    # Ensure audio data is in correct format (float32, normalized)
                    audio_data = audio_data.flatten().astype(np.float32)

                    # Save audio for debugging
                    wavio.write("debug_audio.wav", audio_data, sample_rate, sampwidth=2)

                    # Transcribe
                    result = model.transcribe(audio_data, language="en")
                    transcribed_text = result["text"].lower()
                    print(f"Transcribed: '{transcribed_text}'")

                    if "stop" in transcribed_text:
                        stop_flag = True
                        print(f"Stopped at line {current_line + 1}")
                        break
    except Exception as e:
        print(f"Error in audio processing: {e}")


def main():
    # Generate audio files
    audio_files = generate_audio_files(podcast_script)

    # Start listening thread
    listen_thread = threading.Thread(target=listen_for_stop)
    listen_thread.daemon = True
    listen_thread.start()

    # Play audio
    play_audio(audio_files)

    # Clean up audio files
    for file in audio_files:
        if os.path.exists(file):
            os.remove(file)
    if os.path.exists("debug_audio.wav"):
        os.remove("debug_audio.wav")


if __name__ == "__main__":
    # Required dependencies: pip install gTTS playsound whisper sounddevice numpy wavio
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
