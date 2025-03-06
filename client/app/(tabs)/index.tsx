import React, { useState } from 'react';
import { View, Button, StyleSheet, Text } from 'react-native';
import { Audio } from 'expo-av';

export default function App() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [playback, setPlayback] = useState<Audio.Sound | null>(null);

  const startWebSocket = () => {
    const clientId = Math.random().toString(36).substring(2);
    const websocket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
    
    websocket.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
    };

    websocket.onmessage = async (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === "audio") {
          // Decode base64 audio data
          const audioBytes = atob(message.data);
          const float32Array = new Float32Array(audioBytes.length / 4);
          const uint8Array = new Uint8Array(audioBytes.length);
          
          // Convert base64 string to Uint8Array
          for (let i = 0; i < audioBytes.length; i++) {
            uint8Array[i] = audioBytes.charCodeAt(i);
          }
          
          // Convert Uint8Array to Float32Array
          for (let i = 0; i < float32Array.length; i++) {
            float32Array[i] = new DataView(uint8Array.buffer).getFloat32(i * 4, true);
          }
          
          // Convert Float32Array to Int16Array for WAV (normalize to [-32768, 32767])
          const int16Array = new Int16Array(float32Array.length);
          for (let i = 0; i < float32Array.length; i++) {
            int16Array[i] = Math.max(-32768, Math.min(32767, Math.round(float32Array[i] * 32767)));
          }
          
          // Create WAV buffer
          const wavBuffer = createWavBuffer(int16Array, message.sample_rate, message.channels);
          const blob = new Blob([wavBuffer], { type: 'audio/wav' });
          const url = URL.createObjectURL(blob);
          
          // Play the audio
          if (playback) {
            await playback.unloadAsync();
          }
          const sound = new Audio.Sound();
          await sound.loadAsync({ uri: url });
          await sound.playAsync();
          setPlayback(sound);
        }
      } catch (error) {
        console.error('Error playing received audio:', error);
      }
    };

    websocket.onclose = () => {
      console.log('WebSocket Disconnected');
      setIsConnected(false);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    setWs(websocket);
  };

  const startRecording = async () => {
    try {
      // Request microphone permission
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        alert('Permission to access microphone was denied');
        return;
      }

      // Configure audio mode
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const recordingObj = new Audio.Recording();
      await recordingObj.prepareToRecordAsync(
        {
          android: {
            extension: '.m4a',
            outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_MPEG_4,
            audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_AAC,
            sampleRate: 44100,
            numberOfChannels: 2,
            bitRate: 128000,
          },
          ios: {
            extension: '.m4a',
            outputFormat: Audio.RECORDING_OPTION_IOS_OUTPUT_FORMAT_MPEG4AAC,
            audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
            sampleRate: 44100,
            numberOfChannels: 2,
            bitRate: 128000,
          },
          isMeteringEnabled: true, // Enable metering for real-time data
        }
      );

      // Start recording
      await recordingObj.startAsync();
      setRecording(recordingObj);
      setIsRecording(true);

      // Send audio data in real-time
      streamAudio(recordingObj);

    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const streamAudio = async (recordingObj) => {
    while (isRecording && ws && ws.readyState === WebSocket.OPEN) {
      try {
        // Note: expo-av doesn't provide direct access to raw audio chunks
        // This is a limitation we'll work around by recording in short bursts
        await new Promise(resolve => setTimeout(resolve, 100)); // 100ms chunks
        // In a real implementation, you'd want to access raw audio buffers
        // For now, we'll simulate with a placeholder
        const audioChunk = new Uint8Array(1024); // Placeholder - replace with actual audio data
        const base64Chunk = btoa(String.fromCharCode(...audioChunk));
        
        ws.send(JSON.stringify({
          type: "audio_chunk",
          data: base64Chunk,
          sample_rate: 44100,
          channels: 2
        }));
      } catch (error) {
        console.error('Error streaming audio:', error);
        break;
      }
    }
  };

  const stopRecording = async () => {
    try {
      if (recording && ws && isConnected) {
        await recording.stopAndUnloadAsync();
        const uri = recording.getURI();
        setRecording(null);
        setIsRecording(false);
      }
    } catch (error) {
      console.error('Failed to stop and send recording:', error);
    }
  };

  React.useEffect(() => {
    return () => {
      if (recording) {
        recording.stopAndUnloadAsync();
      }
      if (ws) {
        ws.close();
      }
    };
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.status}>
        {isConnected ? 'Connected' : 'Disconnected'}
      </Text>
      
      <Button
        title="Start Connection"
        onPress={startWebSocket}
        disabled={isConnected}
      />
      
      <Button
        title={isRecording ? 'Stop and Send' : 'Record'}
        onPress={isRecording ? stopRecording : startRecording}
        disabled={!isConnected}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  status: {
    marginBottom: 20,
    fontSize: 18,
  },
});
