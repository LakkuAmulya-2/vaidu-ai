import { useState, useRef, useCallback } from 'react';
import api from '@/lib/api';

export const useTextToSpeech = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const speak = useCallback(async (text: string, lang: string) => {
    try {
      // Stop any currently playing audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      setIsPlaying(true);

      const formData = new FormData();
      formData.append('text', text);
      formData.append('lang', lang);

      const response = await api.post('/synthesize', formData);

      if (response.success && response.audio) {
        // Convert base64 to blob
        const byteCharacters = atob(response.audio);
        const byteNumbers = new Array(byteCharacters.length);
        
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'audio/mp3' });
        const url = URL.createObjectURL(blob);

        // Create and play audio
        const audio = new Audio(url);
        audioRef.current = audio;

        audio.onended = () => {
          setIsPlaying(false);
          URL.revokeObjectURL(url);
          audioRef.current = null;
        };

        audio.onerror = () => {
          setIsPlaying(false);
          URL.revokeObjectURL(url);
          audioRef.current = null;
        };

        await audio.play();
      }
    } catch (error) {
      console.error('TTS error:', error);
      setIsPlaying(false);
    }
  }, []);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
    }
  }, []);

  return { speak, stop, isPlaying };
};
