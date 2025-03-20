// src/App.js
import { useState, useEffect, useRef } from "react";
import { useReactMediaRecorder } from "react-media-recorder";

function App() {
  const [promptText, setPromptText] = useState("");
  const socketRef = useRef(null);

  const [dialogues, setDialogues] = useState([]); // New state for parsed dialogues
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(-1); // -1 is none playing

  // --- playback
  const audioRef = useRef(null);
  const [preloadBuffer, setPreloadBuffer] = useState(0);
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
      const message = JSON.parse(event.data);

      // -- store convo script locally
      if (message.action == "convo_transcript") {
        const newText = message.transcript;
        setResponseText(newText);
        localStorage.setItem("responseText", newText);
        setIsLoading(false);

        parseDialogues(newText); // Parse new text when received. save to dialogue

        console.log("set 0 index and start playback. buffer to 2");
        setCurrentSentenceIndex(0); // Start with first sentence
        setPreloadBuffer(2); // initially request 2 sentences as a buffer window
        setStartPlayback(true); // start playback -- playback useEffect to send to tts server
      }
      // -- audio parse and playback
      else if (message.action === "tts_response") {
        // Convert base64 audio back to binary
        const binaryAudio = atob(message.audio);

        // Convert binary string to Uint8Array
        const bytes = new Uint8Array(binaryAudio.length);
        for (let i = 0; i < binaryAudio.length; i++) {
          bytes[i] = binaryAudio.charCodeAt(i);
        }

        // Create audio blob
        const audioBlob = new Blob([bytes], { type: "audio/mp3" });

        console.log("adding index to sentenceIdx", message.sentenceIndex);

        // Add to queue with correct index
        setAudioQueue((prevQueue) =>
          [
            ...prevQueue,
            {
              blob: audioBlob,
              sentenceIndex: message.sentenceIndex,
            },
          ].sort((a, b) => a.sentenceIndex - b.sentenceIndex)
        ); // Keep queue ordered
      } else if (message.action === "error") {
        console.error("TTS server error:", message.message);
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

  // --- convo playback useEffect
  // send to tts server for tts
  useEffect(() => {
    // works
    if (startPlayback && currentSentenceIndex >= 0) {
      for (let i = 0; i < preloadBuffer; i++) {
        const idx = currentSentenceIndex + i;

        const [host, dialogue] = dialogues[idx];
        console.log("sending to server ------------", idx);
        if (
          socketRef.current &&
          socketRef.current.readyState === WebSocket.OPEN
        ) {
          socketRef.current.send(
            JSON.stringify({
              action: "tts",
              host,
              dialogue,
              idx,
            })
          );
        }
      }
      // console.log("Q len not 0");
      // const [host, dialogue] = dialogues[currentSentenceIndex];
      // console.log("playing ------------", host, dialogue);
      // if (
      //   socketRef.current &&
      //   socketRef.current.readyState === WebSocket.OPEN
      // ) {
      //   socketRef.current.send(
      //     JSON.stringify({
      //       action: "tts",
      //       host,
      //       dialogue,
      //     })
      //   );
      // }
    }
  }, [startPlayback, currentSentenceIndex, dialogues]);

  // -- audio playback useEffect
  // if audio in queue, then show visualizer and play
  useEffect(() => {
    console.log("queue updated");

    if (preloadBuffer == 2) {
      console.log("pre buffer is 2, setting to 1");
      setPreloadBuffer(1);
    }

    if (audioQueue.length > 0 && !audioRef.current) {
      console.log("starting playback for 0th element from queue");
      // --- load audio from Q and play with context
      const audioItem = audioQueue[0];
      const audioUrl = URL.createObjectURL(audioItem.blob);
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

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

      console.log("playing audio");
      audio
        .play()
        .then(() => {
          draw();
          audio.onended = () => {
            console.log("audio has ended, removing element from queue");
            // clear blob from audioQueue to make room for next
            setAudioQueue((prevQueue) => {
              const updatedQueue = prevQueue.slice(1);
              console.log(`Updated queue length: ${updatedQueue.length}`);
              return updatedQueue;
            });
            URL.revokeObjectURL(audioUrl);
            audioRef.current = null; // Clear the reference

            // if handling interruption -> play interruption audio
            // else play next in line
            if (!handleInterruption) {
              // Move to the next dialogue
              setCurrentSentenceIndex((prevIndex) => {
                let nextIndex = 0;
                if (preloadBuffer == 1) {
                  nextIndex = prevIndex + 1;
                } else {
                  nextIndex = prevIndex + 2;
                }
                console.log(
                  "played last",
                  prevIndex,
                  "\nplay next:::",
                  nextIndex
                );

                if (nextIndex < dialogues.length) {
                  console.log("Moving to next dialogue:", dialogues[nextIndex]);
                } else {
                  console.log("All dialogues have been played.");
                  setStartPlayback(false); // Stop playback if all dialogues are done
                }
                return nextIndex;
              });
            } else {
              setHandleInterruption(false);
              console.log("interruption handled");
            }
          };
        })
        .catch((error) => console.error("Audio playback error:", error));
    } else if (audioQueue.length > 0 && audioRef.current) {
      console.log("Skipping playback: audio already playing");
    } else if (audioQueue.length === 0 && !audioRef.current) {
      console.log("Skipping playback: queue empty");
    }
  }, [audioQueue, handleInterruption, dialogues, preloadBuffer]);

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
        // handle interruptions
        setHandleInterruption(true);

        // Stop the currently playing audio
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0; // Reset playback position
          audioRef.current = null; // Clear the reference
        }

        // Clear the audio queue to prevent playback of other media
        setAudioQueue([]);
        // send handle interruption text to server
        if (
          socketRef.current &&
          socketRef.current.readyState === WebSocket.OPEN
        ) {
          socketRef.current.send(
            JSON.stringify({
              action: "tts",
              host: "Host1",
              dialogue: "Whats on your mind?",
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
      startRecording();
    } else if (status === "recording") {
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
