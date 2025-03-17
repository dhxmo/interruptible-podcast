# untitled project: Interruptible Podcast

    TTS altrnatives
#1 -- gpu in real time
  - https://github.com/daswer123/xtts-api-server/tree/main  --- GPU based
  - CPU based -- not the best, but fast and real time
    - https://github.com/rhasspy/rhasspy3/
    - https://github.com/rhasspy/piper/
    - https://github.com/rhasspy/wyoming-piper?tab=readme-ov-file

  - rickman : https://www.youtube.com/watch?v=FVf4vgK1NIA

#2 -- cpu in real time
  - ** https://github.com/remsky/Kokoro-FastAPI
    - streaming implementation in ~/Builds/builds/untitled-v2-text-chunking-On-Device-Speech-to-Speech-Conversational-AI

voice 1: 0.116 * am_adam + 0.775 * am_michael + 0.109 * bm_george
voice 2: 0.6 * af_alloy + 0.4 * af_heart

```
            > News-like – Factual, objective, and serious.
            > Historical – Narrative-driven, often analytical.
            > Scientific – Data-driven, expert-led, sometimes technical.
            > Explainer – Simplified breakdowns of complex topics.
            > Opinionated - Strong personal takes on topics.
            > Dramatic – Intense, theatrical, or emotionally charged.
            > Personal / Memoir – First-person storytelling, diary-style.
            > Meditative / Mindfulness – Calm, reflective, often guided practices.
            > Philosophical / Thoughtful – Deep discussions on abstract topics.
            > Tech & Futurism – Discussing innovations and future trends.
```



STT: faster-whisper or whisper ggml-large-v2
Text-generation: Llama 3 8B Instruct (Q4_K_M) or ollama mistral7b, qwen2.5, llama3.2, deepseekr1 (test and find best for our task)


currently asyncio blocking
for production create multi-processing. everything happens as and when resources available in parallel


# Note on creating samples for quality voice cloning
The following post is a quote by user [Material1276 from reddit](https://www.reddit.com/r/Oobabooga/comments/1807tsl/comment/ka5l8w9/?share_id=_5hh4KJTXrEOSP0hR0hCK&utm_content=2&utm_med    ium=android_app&utm_name=androidcss&utm_source=share&utm_term=1)
> Some suggestions on making good samples
> Keep them about 7-9 seconds long. Longer isn't necessarily better.
> Make sure the audio is down sampled to a Mono, 22050Hz 16 Bit wav file. You will slow down processing by a large % and it seems cause poor quality results otherwise (based on a few tes    ts). 24000Hz is the quality it outputs at anyway!
> Using the latest version of Audacity, select your clip and Tracks > Resample to 22050Hz, then Tracks > Mix > Stereo to Mono. and then File > Export Audio, saving it as a WAV of 22050Hz
> If you need to do any audio cleaning, do it before you compress it down to the above settings (Mono, 22050Hz, 16 Bit).
> Ensure the clip you use doesn't have background noises or music on e.g. lots of movies have quiet music when many of the actors are talking. Bad quality audio will have hiss that needs     clearing up. The AI will pick this up, even if we don't, and to some degree, use it in the simulated voice to some extent, so clean audio is key!
> Try make your clip one of nice flowing speech, like the included example files. No big pauses, gaps or other sounds. Preferably one that the person you are trying to copy will show a l    ittle vocal range. Example files are in [here](https://github.com/oobabooga/text-generation-webui/tree/main/extensions/coqui_tts/voices)
> Make sure the clip doesn't start or end with breathy sounds (breathing in/out etc).
> Using AI generated audio clips may introduce unwanted sounds as its already a copy/simulation of a voice, though, this would need testing.