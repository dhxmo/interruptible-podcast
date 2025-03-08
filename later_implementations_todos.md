1. voice to text on server rather than client
Interruption Detection:
- Integrate Whisper (e.g., Tiny) for real-time STT with VAD (e.g., WebRTC VAD).
- Trigger on voice detection instead of manual input.
- https://github.com/SYSTRAN/faster-whisper
  - https://github.com/GRVYDEV/S.A.T.U.R.D.A.Y/blob/18b40f751bb663f4d8f9fe01c58772aa59f831a4/stt/servers/faster-whisper-api/FastapiServer.py#L45
- ** https://github.com/DongKeon/webrtc-whisper-asr
- Optimize STT (e.g., Distil-Whisper + GPU) for <100ms latency.
- Fine-tune VAD (e.g., Silero) for zero false positives/negatives.
- Add a button interrupt.
- whisper stream: 
  - https://github.com/QuentinFuxa/whisper_streaming_web