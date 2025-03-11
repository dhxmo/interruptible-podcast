# untitled project: Interruptible Podcast

# Stage 1
Goal: A working pipeline with minimal features—just enough to prove the concept. It’s rough, unpolished, and 
single-threaded, but it handles an interruption end-to-end.

1. [x] Podcast Playback:
- Pre-generate a static podcast script (e.g., 5 lines of dialogue).
- Play it as audio using a simple TTS system (e.g., gTTS).
- Store the current position (line number) when interrupted with a whisper voice recognition, keyword "STOP"

2. [x] Interruption Detection:
- Use a basic trigger (e.g., keyboard press like “i” for interrupt, or a hardcoded STT stub).
- Pause the playback when triggered.

3. [x] Response Generation:
- Take a hardcoded user input (e.g., “What’s the source?”).
- Call Ollama’s API with a simple prompt (current line + question).
- Convert response to audio with TTS.

4. [x] Context Resumption:
- Resume playback from the next line after the response.
- No dynamic rewriting—just pick up where it left off.

### TDD Plan:
Tests:
- [x] test_play_podcast: Audio starts and plays a line.
- [x] test_interrupt_stops_playback: Interrupt halts audio at the right spot.
- [x] test_response_generation: Mock Ollama qwen:0.5b API returns a response, TTS plays it.
- [x] test_resume_podcast: Playback resumes at next line after response.

5. Integrate client with server and tie the workflow 
You run the program, hear a podcast line (e.g., “CO2 hit 420 ppm…”) on the phone, press record button to interrupt, 
say a question, hear a response (e.g., “That’s from NOAA”), and the podcast resumes with the next line where it was cut off. 
It’s clunky—manual interrupts, no real STT, no context adjustment—but it works.


# Stage 2: Intermediate – Robust Pipeline
Goal: Add real-time STT, basic context awareness, and smoother transitions. It’s more usable but not fully polished.

Components:

1. LLM + deep-research
- check which one integrates better and integrate:
   - https://github.com/langchain-ai/ollama-deep-researcher
   - https://github.com/zilliztech/deep-searcher
- send research to OS Large model and generate podcast script 

2. Podcast Playback:
- Stream audio in chunks (e.g., 2-3 seconds ahead) instead of pre-rendering everything.
- Track state (line + timestamp) more precisely.
- voice clone: 
  - https://github.com/daswer123/xtts-api-server/tree/main 
  - rickman : https://www.youtube.com/watch?v=FVf4vgK1NIA

3. Response Generation:
- Pass podcast context (last 1-2 lines + next 1-2 lines) + user question to Ollama qwen:0.5b.
- Handle off-topic questions with a fallback (e.g., “Let’s stick to the topic”).
- Play response with TTS, overlapping API call with a buffer phrase (e.g., “Good question…”).
- if answer not known about a question, ask "Would you like me to look this up?". wait for response
	 if yes, look it up online (TODO: online web search without detailed report) -> https://python.langchain.com/docs/integrations/tools/ddg/
		 respond by combining the answer and the next point in transcript

4. Podcast Generation:
- Generate podcast script from detailed report
- keep context across chunks 
- https://github.com/souzatharsis/podcastfy

5. Context Resumption:
- Basic script adjustment: Ollama qwen:0.5b suggests a transition phrase (e.g., “Back to CO2… . flow back to next talking point”).
- Resume from the interrupted point or next logical spot.

6. User Speech to text Whisper stream
- https://github.com/DongKeon/webrtc-whisper-asr


### TDD Plan:
Tests:
- test_deep_research: Create detailed report from a topic
- test_stream_podcast: Streams chunks and tracks position.
- test_search_web_for_topic: Search web for topic and return a summary response ()
- test_contextual_response: Mock ollama:0.5b uses context, returns relevant answer.
- test_podcast_generation: Generate podcast script from detailed report
- test_transition_resumption: Resumes with a transition phrase.

Done Looks Like:
You start the podcast (“CO2 hit 420 ppm…”), say “Where’s that from?”, it pauses, responds (using vectordb of 
the generated report -- "don't know for sure" if answer not known) (“NOAA data”), and resumes (“So, that CO2 spike…”). 
STT works, responses are on-topic, but transitions might feel stiff, and latency could be noticeable.

# Stage 3: Fully Refined – Polished Product
Goal: A seamless, human-like experience with low latency, dynamic rewriting, and professional audio flow.

Components:

1. Podcast Playback
- Generate main script with Large model, save complete script.
- Use high-quality TTS (xtts on local) with natural intonation.
- Pay attention to the voice cloning instructions in xtts-server: Note on creating samples for quality voice cloning
- Fade audio in/out at interrupts for polish.
- add received/send audio to a queue from/to websockets
- collect stream in a queue for 4 seconds and then stream the first 2 seconds and iterate sliding window to always keep 2 seconds in buffer.
- https://github.com/KoljaB/RealtimeTTS

2. Response Generation:
- Full context awareness: Pass entire script history + source material summary to ollama qwen.
- Dynamic tone matching (casual, formal, etc.) based on podcast style.
- Pre-generate fallback responses for common off-topic questions.
- Produce taking user input into consideration for tone 
    - split user input  for topic and tone
        - send topic for the usual processing. use tone to inform the podcast script
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

3. Context Resumption:
- Rewrite the script post-interruption with Ollama qwn:0.5b for seamless integration (e.g., weave the answer into the next segment).
- Randomize transition phrases for variety.
- Smooth audio splicing with fades and overlaps.


### TDD Plan:
Tests:
- test_real_time_script: Script generates ahead, adapts to interrupts.
- test_dynamic_rewrite: Mock qwen rewrites script based on response.
- test_audio_polish: Fades and transitions sound natural.

Done Looks Like:
You’re listening (“CO2 hit 420 ppm…”), say “Source?”, it fades out, responds (“NOAA’s Mauna Loa—great catch!”), and 
resumes (“With that 420 ppm driving storms…”). It’s fast, smooth, and sounds like a real host reacting live.


timeline:
MVP: 1-2 days if STT stubs are fast, focusing on playback and qwen.
Intermediate: 3-5 days to integrate STT and basic context, tweaking as you go.
Refined: 5-7 days for polish, depending on hardware and API speed.


# PROGRESS REPORT

9th Mar '25: 0113
the MVP on the server side was relatively simple. the client is messing with me. tried react native, but that stupid 
framework doesnt have access to the core audio player API, so i'm not able to buffer the audio received from the server.
decided to take a couple days to study webRTC and kotlin properly. will study for the next 3 days, and start implementation 
again starting 11th
Minor setback. will accelerate past it.
