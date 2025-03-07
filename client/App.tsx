import React, { useRef, useEffect, useState } from 'react';
import { Button, PermissionsAndroid, Platform, Text, View } from 'react-native';
import {
  RTCIceCandidate,
  RTCPeerConnection,
  RTCSessionDescription,
} from 'react-native-webrtc';
import io from 'socket.io-client';
import AudioRecord from 'react-native-audio-record';


const configuration = {
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
};

function App(): React.JSX.Element {
  const [isStreaming, setIsStreaming] = useState(false);
  const [transcription, setTranscription] = useState('');

  // const [localStream, setLocalStream] = useState(null);
  const peerConnection = useRef(null);
  const dataChannel = useRef(null);
  const isWebRTCReady = useRef(false); // ✅ Track WebRTC readiness

  const SIGNALING_SERVER_URL = 'http://192.168.0.105:3500';
  const socket = io(SIGNALING_SERVER_URL);



  useEffect(() => {
    // ✅ Request Microphone Permission (Android)
    const requestMicrophonePermission = async () => {
      if (Platform.OS === 'android') {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
          {
            title: 'Microphone Permission',
            message: 'This app needs access to your microphone to record audio.',
            buttonPositive: 'OK',
          }
        );

        if (granted === PermissionsAndroid.RESULTS.GRANTED) {
          console.log('🎙️ Microphone permission granted.');
        } else {
          console.error('🚨 Microphone permission denied.');
        }
      }
    };

    const startWebRTC = async () => {
      console.log('🚀 Connecting to Signaling Server...');

      socket.on('connect', () => console.log('✅ Connected to Signaling Server!'));

      peerConnection.current = new RTCPeerConnection(configuration);

      dataChannel.current = peerConnection.current.createDataChannel('audio');
      console.log('📡 Created DataChannel:', dataChannel.current);

      // ✅ Ensure DataChannel event bindings happen immediately
      dataChannel.current.onopen = () => {
        console.log('✅ DataChannel Open - Ready to send audio!');
        isWebRTCReady.current = true; // ✅ Mark WebRTC as ready
      };

      dataChannel.current.onclose = () => {
        console.log('❌ DataChannel Closed!');
        isWebRTCReady.current = false; // Reset WebRTC status
      };

      dataChannel.current.onerror = (error) => console.error('🚨 DataChannel Error:', error);

      dataChannel.current.onmessage = (event) => {
        console.log('📜 Received Transcription:', event.data);
      };

      // Send ICE candidates to signaling server
      peerConnection.current.onicecandidate = (event) => {
        if (event.candidate) {
          console.log('🌍 Sending ICE Candidate:', event.candidate);
          socket.emit('ICEcandidate', { candidate: event.candidate });
        }
      };

      // ✅ Wait for remote SDP Answer before proceeding
      socket.on('sdp', async (data) => {
        console.log(`📡 Received SDP: ${data.type}`);
        if (data.type === 'answer') {
          await peerConnection.current.setRemoteDescription(new RTCSessionDescription(data));
          console.log('✅ SDP Answer Applied!');
          isWebRTCReady.current = true; // ✅ Mark WebRTC as ready
        }
      });

      // Handle ICE Candidates from Server
      socket.on('ICEcandidate', async (data) => {
        console.log(`🌍 Received ICE Candidate:\n${JSON.stringify(data)}`);
        if (data.candidate) {
          await peerConnection.current.addIceCandidate(new RTCIceCandidate(data.candidate));
        }
      });

      // Handle transcriptions
      socket.on('transcription', (data) => {
        console.log('Received transcription:', data);
        setTranscription(data.text);
      });

      // Create SDP Offer and wait for SDP Answer
      const offer = await peerConnection.current.createOffer();
      await peerConnection.current.setLocalDescription(offer);
      console.log('📤 Sending SDP Offer:', offer);
      socket.emit('sdp', offer);
    };

    requestMicrophonePermission();
    startWebRTC();

    return () => {
      peerConnection.current?.close();
      dataChannel.current?.close();
      console.log('Cleanup: WebRTC and WebSocket closed');
    };
  }, []);

  // ✅ Start Recording and Sending PCM via DataChannel
  const startStreaming = async () => {
    console.log('🎙️ Initializing Audio Record...');

    const options = {
      sampleRate: 16000,
      channels: 1,        // Mono
      bitsPerSample: 16,  // 16-bit PCM
      audioSource: 6,     // android only (see below)
      bufferSize: 4096,    // default is 2048
    };

    AudioRecord.init(options);

    AudioRecord.start();

    AudioRecord.on('data', data => {
      if (dataChannel.current?.readyState === 'open') {
        // const pcmChunk = Buffer.from(data, "base64"); // Decode base64 → PCM bytes
        dataChannel.current.send(data);
      } else {
        console.warn("⚠️ DataChannel not open, can't send audio.");
      }
    });

    setIsStreaming(true);
  };

  // ✅ Stop Recording
  const stopStreaming = async () => {
    console.log('🛑 Stopping stream...');
    AudioRecord.stop();
    dataChannel.current?.close();
    setIsStreaming(false);
  };

  return (
    <View>
      <Button title={isStreaming ? 'Stop Streaming' : 'Start Streaming'} onPress={isStreaming ? stopStreaming : startStreaming} />
      <Text>Transcription: {transcription}</Text>
    </View>
  );
}

export default App;
