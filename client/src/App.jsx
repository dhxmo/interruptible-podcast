// src/App.js
import { useState, useEffect, useRef } from "react";
import { useReactMediaRecorder } from "react-media-recorder";

function App() {
  const [promptText, setPromptText] = useState("");
  const socketRef = useRef(null);

  const [dialogues, setDialogues] = useState([]); // New state for parsed dialogues
  const dialoguesRef = useRef([]);

  // --- playback
  const [isLoading, setIsLoading] = useState(false);
  const [showPlayerView, setShowPlayerView] = useState(false);

  const currentIndexRef = useRef(0);
  const audioQueueRef = useRef([]); // will store Audio objects
  const isPlayingRef = useRef(false);
  const audioRef = useRef(null); // currently playing audio

  // --- interruption related
  const isHandleInterruption = useRef(false);
  const interruptionQueueRef = useRef([]);
  const resumeIndexRef = useRef(0);

  // sockets
  useEffect(() => {
    socketRef.current = new WebSocket("ws://localhost:8000/ws");

    socketRef.current.onopen = () => {
      console.log("WebSocket connected");
    };

    socketRef.current.onmessage = (event) => {
      handleSocketMessage(event);
    };

    socketRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
    socketRef.current.onclose = () => console.log("WebSocket closed");

    return () => {
      socketRef.current?.close();
    };
  }, []);

  //! [FLOW] - stars here
  function handleSocketMessage(event) {
    try {
      const message = JSON.parse(event.data);

      // -- store convo script locally, parse and store to dialoguesRef
      if (message.action == "convo_transcript") {
        const newText = message.transcript;
        localStorage.setItem("responseText", newText);
        setIsLoading(false);
        parseDialogues(newText); // Parse new text when received. save to dialogue
      }
      // -- receive audio after tts
      else if (message.action === "tts_response") {
        if (!message.audio || message.audio.length < 100) {
          console.error("Received empty or invalid audio payload", message);
          return;
        }

        // Convert base64 audio back to binary
        const binaryAudio = atob(message.audio);

        // Convert binary string to Uint8Array
        const bytes = new Uint8Array(binaryAudio.length);
        for (let i = 0; i < binaryAudio.length; i++) {
          bytes[i] = binaryAudio.charCodeAt(i);
        }

        // ---  Create audio blob and add to queue
        const audioBlob = new Blob([bytes], { type: "audio/mp3" });
        const audio = new Audio(URL.createObjectURL(audioBlob));
        audioQueueRef.current.push(audio);
        audio.onended = () => handleAudioEnded(); // when this finishes, play next

        // ---  If nothing is playing, start playback if not handling interruption
        if (!isPlayingRef.current && !isHandleInterruption.current) {
          playNext();
        }
      }
      // --- handle interruption
      else if (message.action === "interruption_tts_response") {
        isPlayingRef.current = false; // stop any audio playback from the script

        // parse audio from base64 to blob
        const binaryAudio = atob(message.audio);
        const bytes = new Uint8Array(binaryAudio.length);
        for (let i = 0; i < binaryAudio.length; i++) {
          bytes[i] = binaryAudio.charCodeAt(i);
        }
        const audioBlob = new Blob([bytes], { type: "audio/mp3" });
        const audio = new Audio(URL.createObjectURL(audioBlob));

        interruptionQueueRef.current.push(audio); // add audio to interruption queue to playback on priority

        // If not playing anything currently, start playing interruption response
        if (isHandleInterruption.current) {
          playInterruptionQueue();
        }
      } else if (message.action === "error") {
        console.error("TTS server error:", message.message);
      }

      setShowPlayerView(true);
    } catch (err) {
      "error in handle socket msg", err.message;
    }
  }

  // on setting dialogues for the first time, begin:::
  useEffect(() => {
    dialoguesRef.current = dialogues;

    if (dialogues.length > 0) {
      preloadNext(socketRef.current);
    }
  }, [dialogues]);

  // Parse dialogue text into [speaker, dialogue] pairs
  // each dialogue is broken up into individual sentence for faster tts
  function parseDialogues(script) {
    const lines = script
      .trim()
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => line.trim());

    // --- split on punctuation based each sentence. can get jaggy
    // const sentenceRegex = /[^.!?]+[.!?]?/g; // Regex to break text into sentences
    // const parsedDialogues = [];

    // lines.forEach((line) => {
    //   const [speaker, ...dialogueParts] = line.split(":");
    //   const dialogue = dialogueParts.join(":").trim();

    //   // Split dialogue into sentences
    //   const sentences = dialogue.match(sentenceRegex) || [dialogue];

    //   sentences.forEach((sentence) => {
    //     const trimmedSentence = sentence.trim();
    //     if (trimmedSentence) {
    //       parsedDialogues.push([speaker.trim(), trimmedSentence]);
    //     }
    //   });
    // });
    // setDialogues(parsedDialogues);

    // -- split according to person
    const parsedDialogues = lines.map((line) => {
      const [speaker, ...dialogueParts] = line.split(":"); // Split at first colon
      return [speaker, dialogueParts.join(":").trim()]; // Rejoin dialogue in case it contains colons
    });

    setDialogues(parsedDialogues);
  }

  // --- send all dialogues for tts
  // sending all ensures smooth playback
  function preloadNext(socket) {
    while (
      currentIndexRef.current < dialoguesRef.current.length &&
      audioQueueRef.current.length < 2 &&
      socket?.readyState === WebSocket.OPEN
    ) {
      const [host, dialogue] = dialoguesRef.current[currentIndexRef.current];
      currentIndexRef.current += 1;
      socket.send(
        JSON.stringify({
          action: "tts",
          host,
          dialogue,
          idx: currentIndexRef.current,
        })
      );
    }
  }

  // --- play next script audio file form the audioQueue
  function playNext() {
    if (audioQueueRef.current.length > 0) {
      const nextAudio = audioQueueRef.current.shift();
      audioRef.current = nextAudio;
      isPlayingRef.current = true;
      nextAudio.play();
      resumeIndexRef.current += 1; // update each time audio plays from the script. running counter for current play index to send for interruption
    } else {
      isPlayingRef.current = false;
    }
  }

  // --- play the next audio file in the audioQ
  function handleAudioEnded() {
    isPlayingRef.current = false;
    playNext(); // Play the next audio in the queue
  }

  // --- recording user interruption and sending to server
  const { status, startRecording, stopRecording, error } =
    useReactMediaRecorder({
      audio: {
        echoCancellation: true,
        noiseSuppression: false, // Adjust based on testing
        autoGainControl: true,
        sampleRate: 16000,
      },
      blobPropertyBag: { type: "audio/webm" },
      onStop: (blobUrl, blob) => {
        // Send to server
        if (
          socketRef.current &&
          socketRef.current.readyState === WebSocket.OPEN
        ) {
          socketRef.current.send(
            JSON.stringify({
              action: "init_interruption",
              next_sentence: dialoguesRef.current[resumeIndexRef.current],
            })
          );
          socketRef.current.send(blob);
        }
      },
    });

  // Log recording status and errors
  useEffect(() => {
    console.log("Recording status:", status);
    if (error) console.error("Recording error:", error);
  }, [status, error]);

  // --- record user interruption
  function handleTalkClick() {
    if (status === "idle" || status === "stopped") {
      // --- Pause current playing audio
      if (audioRef.current) {
        audioRef.current.pause();
      }
      // Store current playback index
      // resumeIndexRef.current = currentIndexRef.current - 1; // The one that was playing
      // Clear interruption queue
      interruptionQueueRef.current = [];

      // set flag
      isHandleInterruption.current = true;

      // Play custom interruption prompt and start recording after play
      const interruptionPrompt = new Audio("/interruption_audio.wav");
      interruptionPrompt.onended = () => startRecording(); // start recording on interruption audio end
      interruptionPrompt.play();
    } else if (status === "recording") {
      stopRecording();
    }
  }

  // --- load interruption audio onto context
  function playInterruptionQueue() {
    if (interruptionQueueRef.current.length > 0) {
      const nextAudio = interruptionQueueRef.current.shift();
      audioRef.current = nextAudio;
      isPlayingRef.current = true;
      nextAudio.play();

      // on interruption audio end, play the next script playback
      nextAudio.onended = () => {
        isHandleInterruption.current = false;
        playNext();
      };
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({ action: "submit_prompt", prompt: promptText })
      );
      setPromptText("");
      setIsLoading(true);
    }
  }

  function handleBack() {
    setShowPlayerView(false);
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>AIR</h1>
      {!showPlayerView ? (
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={promptText}
            onChange={(e) => setPromptText(e.target.value)}
            placeholder="What do you wanna talk about?"
            style={{ width: "300px", padding: "8px", marginRight: "10px" }}
          />
          <button
            type="submit"
            disabled={isLoading}
            style={{ padding: "8px 16px", marginLeft: "10px" }}
          >
            {isLoading ? "Loading..." : "Submit"}
          </button>
        </form>
      ) : (
        <div>
          <button
            onClick={handleBack}
            style={{ padding: "8px 16px", marginBottom: "20px" }}
          >
            Back
          </button>
          <canvas
            width="300"
            height="100"
            style={{ border: "1px solid #ccc", marginBottom: "20px" }}
          />
          <button onClick={handleTalkClick} style={{ padding: "8px 16px" }}>
            {status === "recording" ? "Stop Recording" : "Talk"}
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
