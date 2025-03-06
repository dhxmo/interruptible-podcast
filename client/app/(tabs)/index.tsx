import React, { useState, useEffect } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { Audio } from 'expo-av';


export default function HomeScreen() {
  const [recording, setRecording] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const socketRef = React.useRef<WebSocket | null>(null);

  const startWebSocket = async () => {
    try {
      const clientId = Math.random().toString(36).substring(2);
      socketRef.current = new WebSocket(`ws://192.168.0.105:8000/api/v1/ws/${clientId}`);
      
      socketRef.current.onopen = () => {
        console.log('WebSocket Connected');
        setIsConnected(true);
      };
  
      socketRef.current.onmessage = async (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === "audio") {
            const audioBytes = atob(message.data);
            const arrayBuffer = new Uint8Array(audioBytes.length);
            for (let i = 0; i < audioBytes.length; i++) {
              arrayBuffer[i] = audioBytes.charCodeAt(i);
            }
            
            const blob = new Blob([arrayBuffer], { type: 'audio/m4a' });
            const url = URL.createObjectURL(blob);
            const sound = new Audio.Sound();
            await sound.loadAsync({ uri: url });
            await sound.playAsync();
          }
        } catch (error) {
          console.error('Error processing message:', error);
        }
      };
  
      socketRef.current.onclose = (event) => {
        console.log('WebSocket Closed:', event.code, event.reason);
        setIsConnected(false);
      };
  
      socketRef.current.onerror = (error) => {
        console.error('WebSocket Error:', error);
        setIsConnected(false);
      };
    } catch (error) {
      console.error("WebSocket setup error:", error);
    }
  };


  // Cleanup on unmount
  useEffect(() => {
    return () => {
      socketRef.current?.close();
    };
  }, []);

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        alert('Permission to access microphone was denied');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const recordingObj = new Audio.Recording();
      await recordingObj.prepareToRecordAsync();
      await recordingObj.startAsync();
      
      setRecording(recordingObj);
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const stopAndSendRecording = async () => {
    try {
      if (recording && socketRef.current && isConnected) {
        // TODO: send user recorded audio to server here 

        if (!recording) return;

        await recording.stopAndUnloadAsync();
        const uri = recording.getURI();
        const response = await fetch(uri);
        const blob = await response.blob();
        console.log("blob", blob);
        
        // Convert blob to array buffer and send as binary data
        const arrayBuffer = await blob.arrayBuffer();
        const byteArray = new Uint8Array(arrayBuffer);
        console.log("byteArray", byteArray, socketRef.current);

        socketRef.current?.send(byteArray);

        setRecording(null);
        setIsRecording(false);
      }
    } catch (error) {
      console.error('Failed to stop and send recording:', error);
    }
  };

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
        title={recording ? 'Stop Recording' : 'Start Recording'}
        onPress={recording ? stopAndSendRecording : startRecording}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  stepContainer: {
    gap: 8,
    marginBottom: 8,
  },
  reactLogo: {
    height: 178,
    width: 290,
    bottom: 0,
    left: 0,
    position: 'absolute',
  },
});
