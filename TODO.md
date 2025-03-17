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