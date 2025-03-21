import requests
import io
import logging


class Config:
    xtts_server_endpoint = "http://172.219.157.164:14930/generate-audio/"


# Sample data
sentence = "Right? But then I started thinking about how this thing could hack into a TIE Fighter's systems. Can you imagine?"
speaker = "clint"  # Assuming this maps to a file path in speaker_lookup
# speaker_lookup = {"clint": "voices/clint.wav"}

# Prepare request parameters
params = {"text": sentence, "speaker": speaker, "language": "en"}

# Buffer to hold the audio data
audio_buffer = io.BytesIO()

# Send the request
response = requests.get(Config.xtts_server_endpoint, params=params, stream=True)
if response.status_code == 200:
    # Write streamed chunks to the buffer
    for chunk in response.iter_content(chunk_size=1024):
        audio_buffer.write(chunk)
    audio_buffer.seek(0)

    # Write the buffer to a file
    with open("interruption_audio.wav", "wb") as f:
        f.write(audio_buffer.read())
    print("Audio successfully written to 'output.wav'")
else:
    logging.error(f"Error in tts from server: {response.status_code} - {response.text}")

# Clean up the buffer
audio_buffer.close()
