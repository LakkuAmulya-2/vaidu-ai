import { useState, useRef, useCallback } from 'react';
import api from '@/lib/api';

export const useAudioRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      throw new Error('Microphone access denied');
    }
  }, []);

  const stopRecording = useCallback(async (lang: string): Promise<string> => {
    return new Promise((resolve, reject) => {
      const mediaRecorder = mediaRecorderRef.current;
      
      if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        reject(new Error('No active recording'));
        return;
      }

      mediaRecorder.onstop = async () => {
        setIsRecording(false);
        setIsProcessing(true);

        try {
          const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
          
          // Send to backend for transcription
          const formData = new FormData();
          formData.append('file', audioBlob, 'recording.webm');
          formData.append('lang', lang);

          const response = await api.post('/transcribe', formData);

          if (response.success && response.text) {
            resolve(response.text);
          } else {
            reject(new Error(response.message || 'Transcription failed'));
          }
        } catch (error) {
          console.error('Transcription error:', error);
          reject(error);
        } finally {
          setIsProcessing(false);
          
          // Stop all tracks
          mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.stop();
    });
  }, []);

  return {
    isRecording,
    isProcessing,
    startRecording,
    stopRecording
  };
};
