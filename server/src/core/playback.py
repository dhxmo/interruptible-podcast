# this functionality will live in the client. only implemented here as test

import json
import os
import select
import sys
import time

import keyboard
from gtts import gTTS
import playsound

SCRIPT = [
    "Welcome to our AI-powered podcast!",
    "Today, we explore the future of technology.",
    "AI is changing the world faster than ever.",
    "Let's dive into some amazing innovations.",
    "Thank you for tuning in. See you next time!"
]
PROGRESS_FILE = "progress.json"

def save_progress(user_id, index):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({user_id: index}, f)

def load_progress(user_id):
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f).get(user_id, 0)
    return 0

def text_to_speech(text):
    tts = gTTS(text)
    tts.save("temp.mp3")
    playsound.playsound("temp.mp3")
    os.remove("temp.mp3")

def main():
    user_id = 0
    start_index = load_progress(user_id)
    try:
        for i in range(start_index, len(SCRIPT)):
            print(SCRIPT[i])  # Print for visibility
            text_to_speech(SCRIPT[i])
            time.sleep(1)  # Simulate pause between lines
            sys.stdin.read(1)
            if keyboard.is_pressed("i"):  # Check for interrupt key
                print("\nPlayback interrupted. Progress saved.")
                save_progress(user_id, i)
                break
            save_progress(user_id, i + 1)
        else:
            save_progress(user_id, 0)
    except KeyboardInterrupt:
        print("\nPlayback interrupted manually. Progress saved.")
