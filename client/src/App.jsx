// src/App.js
import { useState, useEffect, useRef } from "react";
import { useReactMediaRecorder } from "react-media-recorder";

function App() {
  const [promptText, setPromptText] = useState("");
  const socketRef = useRef(null);

  const [dialogues, setDialogues] = useState([]); // New state for parsed dialogues
  const dialoguesRef = useRef([]);
  // const [currentSentenceIndex, setCurrentSentenceIndex] = useState(-1); // -1 is none playing

  // // --- playback
  // const audioRef = useRef(null);
  // const [preloadBuffer, setPreloadBuffer] = useState(0);
  // const [startPlayback, setStartPlayback] = useState(false);
  // const [audioQueue, setAudioQueue] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showPlayerView, setShowPlayerView] = useState(false);
  // const [responseText, setResponseText] = useState("");
  // const [handleInterruption, setHandleInterruption] = useState(false);

  const currentIndexRef = useRef(0);
  const audioQueueRef = useRef([]); // will store Audio objects
  const isPlayingRef = useRef(false);
  const audioRef = useRef(null); // currently playing audio

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

  function handleSocketMessage(event) {
    try {
      const message = JSON.parse(event.data);

      // -- store convo script locally
      if (message.action == "convo_transcript") {
        const newText = message.transcript;
        localStorage.setItem("responseText", newText);
        setIsLoading(false);

        console.log("dialogue len", dialogues.length);
        parseDialogues(newText); // Parse new text when received. save to dialogue
      }
      // -- audio parse and playback
      else if (message.action === "tts_response") {
        console.log("audio size: ", message.audio.length);
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

        // Create audio blob and add to queue
        const audioBlob = new Blob([bytes], { type: "audio/mp3" });
        const audio = new Audio(URL.createObjectURL(audioBlob));
        audioQueueRef.current.push(audio);

        audio.onended = () => handleAudioEnded();

        // If nothing is playing, start playback
        if (!isPlayingRef.current) {
          playNext();
        }

        preloadNext(socketRef.current);
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
  const parseDialogues = (script) => {
    const lines = script
      .trim()
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => line.trim());

    const sentenceRegex = /[^.!?]+[.!?]?/g; // Regex to break text into sentences

    const parsedDialogues = [];

    lines.forEach((line) => {
      const [speaker, ...dialogueParts] = line.split(":");
      const dialogue = dialogueParts.join(":").trim();

      // Split dialogue into sentences
      const sentences = dialogue.match(sentenceRegex) || [dialogue];

      sentences.forEach((sentence) => {
        const trimmedSentence = sentence.trim();
        if (trimmedSentence) {
          parsedDialogues.push([speaker.trim(), trimmedSentence]);
        }
      });
    });
    setDialogues(parsedDialogues);
  };

  function preloadNext(socket) {
    while (
      currentIndexRef.current < dialoguesRef.current.length &&
      audioQueueRef.current.length < 2 &&
      socket?.readyState === WebSocket.OPEN
    ) {
      const [host, dialogue] = dialoguesRef.current[currentIndexRef.current];
      console.log("preloading", host, dialogue);

      currentIndexRef.current += 1;
      socket.send(
        JSON.stringify({
          action: "tts",
          host,
          dialogue,
        })
      );
    }
  }

  const playNext = () => {
    if (audioQueueRef.current.length > 0) {
      const nextAudio = audioQueueRef.current.shift();
      audioRef.current = nextAudio;
      isPlayingRef.current = true;
      nextAudio.play();
    } else {
      isPlayingRef.current = false;
    }
  };

  const handleAudioEnded = () => {
    isPlayingRef.current = false;
    playNext(); // Play the next audio in the queue
  };

  // recording user interruption and sending to server
  // const { status, startRecording, stopRecording, error } =
  //   useReactMediaRecorder({
  //     audio: {
  //       echoCancellation: true,
  //       noiseSuppression: false, // Adjust based on testing
  //       autoGainControl: true,
  //       sampleRate: 16000,
  //     },
  //     blobPropertyBag: { type: "audio/webm" },
  //     onStart: () => {
  //       // handle interruptions
  //       setHandleInterruption(true);

  //       // Stop the currently playing audio
  //       if (audioRef.current) {
  //         audioRef.current.pause();
  //         audioRef.current.currentTime = 0; // Reset playback position
  //         audioRef.current = null; // Clear the reference
  //       }

  //       // Clear the audio queue to prevent playback of other media
  //       setAudioQueue([]);
  //       // send handle interruption text to server
  //       if (
  //         socketRef.current &&
  //         socketRef.current.readyState === WebSocket.OPEN
  //       ) {
  //         socketRef.current.send(
  //           JSON.stringify({
  //             action: "tts",
  //             host: "Host1",
  //             dialogue: "Whats on your mind?",
  //           })
  //         );
  //       }
  //     },
  //     onStop: (blobUrl, blob) => {
  //       // Send to server
  //       // TODO: fetch next sentence from the responseText
  //       if (
  //         socketRef.current &&
  //         socketRef.current.readyState === WebSocket.OPEN
  //       ) {
  //         socketRef.current.send(
  //           JSON.stringify({
  //             action: "init_interruption",
  //             next_sentence: "...",
  //           })
  //         );
  //         socketRef.current.send(blob);
  //       }
  //     },
  //   });

  // // Log recording status and errors
  // useEffect(() => {
  //   console.log("Recording status:", status);
  //   if (error) console.error("Recording error:", error);
  // }, [status, error]);

  const handleTalkClick = () => {
    // if (status === "idle" || status === "stopped") {
    //   startRecording();
    // } else if (status === "recording") {
    //   stopRecording();
    // }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({ action: "submit_prompt", prompt: promptText })
      );
      setPromptText("");
      setIsLoading(true);
    }
  };

  const handleBack = () => {
    setShowPlayerView(false);
  };

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
