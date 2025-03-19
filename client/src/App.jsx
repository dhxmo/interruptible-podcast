// src/App.js
import { useState, useEffect, useRef } from "react";
import { useReactMediaRecorder } from "react-media-recorder";

// TODO: comment before this gets out of hand


function App() {
  const [promptText, setPromptText] = useState("");
  const [socket, setSocket] = useState(null);
  const socketRef = useRef(null);

  const [dialogues, setDialogues] = useState([]); // New state for parsed dialogues
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(-1); // -1 is none playing

  // --- playback
  const audioRef = useRef(null);
  const [startPlayback, setStartPlayback] = useState(false);
  const [audioQueue, setAudioQueue] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showPlayerView, setShowPlayerView] = useState(false);
  const [responseText, setResponseText] = useState("");
  const [handleInterruption, setHandleInterruption] = useState(false);

  // sockets
  useEffect(() => {
    socketRef.current = new WebSocket("ws://localhost:8000/ws");

    socketRef.current.onopen = () => {
      console.log("WebSocket connected");
    };

    socketRef.current.onmessage = (event) => {
      if (event.data instanceof Blob) {
        console.log("Received audio blob from WebSocket:", event.data);
        setAudioQueue((prevQueue) => {
          const updatedQueue = [...prevQueue, event.data];
          console.log("Audio queue after receiving new blob:", updatedQueue);
          return updatedQueue;
        });

        if (handleInterruption) setHandleInterruption(false);
      } else {
        const message = JSON.parse(event.data);

        if (message.action == "convo_transcript") {
          const newText = message.transcript;
          setResponseText(newText);
          localStorage.setItem("responseText", newText);
          setIsLoading(false);

          parseDialogues(newText); // Parse new text when received
          setCurrentSentenceIndex(0); // Start with first sentence
          setStartPlayback(true);
        }
      }

      setShowPlayerView(true);
    };

    socketRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
    socketRef.current.onclose = () => console.log("WebSocket closed");

    return () => {
      socketRef.current?.close();
    };
  }, []);

  // Parse dialogue text into [speaker, dialogue] pairs
  const parseDialogues = (script) => {
    const lines = script
      .trim() // Remove leading/trailing whitespace
      .split("\n") // Split into lines
      .filter((line) => line.trim()) // Remove empty lines
      .map((line) => line.trim()); // Trim each line

    const parsedDialogues = lines.map((line) => {
      const [speaker, ...dialogueParts] = line.split(":"); // Split at first colon
      return [speaker, dialogueParts.join(":").trim()]; // Rejoin dialogue in case it contains colons
    });

    setDialogues(parsedDialogues);
  };

  // script submission
  useEffect(() => {
    if (startPlayback && currentSentenceIndex >= 0) {
      const [host, dialogue] = dialogues[currentSentenceIndex];
      console.log("host, dialogue", host, dialogue);
      if (
        socketRef.current &&
        socketRef.current.readyState === WebSocket.OPEN
      ) {
        socketRef.current.send(
          JSON.stringify({
            action: "tts",
            host,
            dialogue,
          })
        );
      }
    }
  }, [startPlayback, currentSentenceIndex]);

  // Playback audio when audioQueue changes --- script playback
  useEffect(() => {
    if (audioQueue.length > 0) {
      console.log("Audio queue before playback:", audioQueue);

      const audioBlob = audioQueue[0];
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      console.log("Playing audio from queue:", audioBlob);

      // Audio visualization setup
      const audioContext = new AudioContext();
      const source = audioContext.createMediaElementSource(audio);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyser.connect(audioContext.destination);

      const canvas = document.querySelector("canvas");
      const ctx = canvas.getContext("2d");
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const draw = () => {
        requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);

        ctx.fillStyle = "rgb(0, 0, 0)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const barWidth = (canvas.width / bufferLength) * 2.5;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
          const barHeight = dataArray[i];
          ctx.fillStyle = `rgb(${barHeight + 100}, 50, 50)`;
          ctx.fillRect(
            x,
            canvas.height - barHeight / 2,
            barWidth,
            barHeight / 2
          );
          x += barWidth + 1;
        }
      };

      audio
        .play()
        .then(() => {
          draw();
          // Handle playback completion
          audio.onended = () => {
            console.log("Audio playback finished for:", audioBlob);
            setAudioQueue((prevQueue) => {
              const updatedQueue = prevQueue.slice(1);
              console.log("Audio queue after playback:", updatedQueue);
              return updatedQueue;
            });
            URL.revokeObjectURL(audioUrl);
            audioRef.current = null; // Clear the reference

            if (!handleInterruption) {
              // Move to the next dialogue
              setCurrentSentenceIndex((prevIndex) => {
                const nextIndex = prevIndex + 1;
                if (nextIndex < dialogues.length) {
                  console.log("Moving to next dialogue:", dialogues[nextIndex]);
                } else {
                  console.log("All dialogues have been played.");
                  setStartPlayback(false); // Stop playback if all dialogues are done
                }
                return nextIndex;
              });
            }
          };
        })
        .catch((error) => console.error("Audio playback error:", error));
    }
  }, [audioQueue, handleInterruption]);

  // recording user interruption and sending to server
  const { status, startRecording, stopRecording, error } =
    useReactMediaRecorder({
      audio: {
        echoCancellation: true,
        noiseSuppression: false, // Adjust based on testing
        autoGainControl: true,
        sampleRate: 16000,
      },
      blobPropertyBag: { type: "audio/webm" },
      onStart: () => {
        console.log("Recording started");

        setHandleInterruption(true);

        // Stop the currently playing audio
        if (audioRef.current) {
          console.log("Stopping current audio playback...");
          audioRef.current.pause();
          audioRef.current.currentTime = 0; // Reset playback position
          audioRef.current = null; // Clear the reference
        }

        // Clear the audio queue
        console.log("Clearing audio queue...");
        setAudioQueue([]);
        console.log("Audio queue after clearing:", audioQueue);

        if (
          socketRef.current &&
          socketRef.current.readyState === WebSocket.OPEN
        ) {
          console.log("sending interruption text");
          socketRef.current.send(
            JSON.stringify({
              action: "tts",
              host: "host1",
              dialogue: "Hey, whatsup ? Whats on your mind?",
            })
          );
        }
      },
      onStop: (blobUrl, blob) => {
        // Send to server
        // TODO: fetch next sentence from the responseText
        if (
          socketRef.current &&
          socketRef.current.readyState === WebSocket.OPEN
        ) {
          socketRef.current.send(
            JSON.stringify({
              action: "init_interruption",
              next_sentence: "...",
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

  const handleTalkClick = () => {
    if (status === "idle" || status === "stopped") {
      console.log("Starting recording...");
      startRecording();
    } else if (status === "recording") {
      console.log("Stopping recording...");
      stopRecording();
    }
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
