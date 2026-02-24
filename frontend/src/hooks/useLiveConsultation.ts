import { useState, useEffect, useRef, useCallback } from 'react';

interface LiveConsultationMessage {
  type: 'text' | 'audio' | 'emergency' | 'tool_call';
  data?: string;
  message?: string;
  reason?: string;
  actions?: Array<{
    action: string;
    priority: string;
    message: string;
  }>;
  tool?: string;
  result?: any;
}

interface UseLiveConsultationReturn {
  isConnected: boolean;
  isConnecting: boolean;
  messages: LiveConsultationMessage[];
  error: string | null;
  connect: () => void;
  disconnect: () => void;
  sendText: (text: string) => void;
  sendAudio: (audioData: ArrayBuffer) => void;
  sendImage: (imageData: string) => void;
  clearMessages: () => void;
}

export const useLiveConsultation = (
  sessionId: string
): UseLiveConsultationReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [messages, setMessages] = useState<LiveConsultationMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  
  const MAX_RECONNECT_ATTEMPTS = 3;
  const RECONNECT_DELAY = 2000;

  const getWebSocketUrl = useCallback(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = apiUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${wsHost}/live-consult/${sessionId}`;
  }, [sessionId]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      const wsUrl = getWebSocketUrl();
      console.log('Connecting to:', wsUrl);
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setIsConnecting(false);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          if (event.data instanceof Blob) {
            // Audio response from Gemini
            const audioBlob = event.data;
            const audioUrl = URL.createObjectURL(audioBlob);
            
            setMessages((prev) => [
              ...prev,
              {
                type: 'audio',
                data: audioUrl,
              },
            ]);
            
            // Auto-play audio
            const audio = new Audio(audioUrl);
            audio.play().catch((err) => {
              console.error('Audio playback failed:', err);
            });
          } else {
            // Text/JSON response
            const data = JSON.parse(event.data);
            setMessages((prev) => [...prev, data]);
            
            // Handle emergency alerts
            if (data.type === 'emergency') {
              // Play alert sound
              const alertAudio = new Audio('/alert.mp3');
              alertAudio.play().catch(() => {
                // Fallback to system beep
                console.log('🚨 EMERGENCY ALERT');
              });
            }
          }
        } catch (err) {
          console.error('Message parsing error:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('Connection error occurred');
        setIsConnecting(false);
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        setIsConnecting(false);
        wsRef.current = null;

        // Auto-reconnect logic
        if (
          !event.wasClean &&
          reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS
        ) {
          reconnectAttemptsRef.current += 1;
          console.log(
            `Reconnecting... Attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS}`
          );
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, RECONNECT_DELAY);
        } else if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
          setError('Connection lost. Please refresh and try again.');
        }
      };
    } catch (err) {
      console.error('Connection failed:', err);
      setError('Failed to connect. Please try again.');
      setIsConnecting(false);
    }
  }, [getWebSocketUrl]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
    reconnectAttemptsRef.current = 0;
  }, []);

  const sendText = useCallback((text: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      setError('Not connected. Please connect first.');
      return;
    }

    try {
      wsRef.current.send(
        JSON.stringify({
          type: 'text',
          data: text,
        })
      );
    } catch (err) {
      console.error('Send text error:', err);
      setError('Failed to send message');
    }
  }, []);

  const sendAudio = useCallback((audioData: ArrayBuffer) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    try {
      wsRef.current.send(audioData);
    } catch (err) {
      console.error('Send audio error:', err);
      setError('Failed to send audio');
    }
  }, []);

  const sendImage = useCallback((imageData: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }

    try {
      wsRef.current.send(
        JSON.stringify({
          type: 'image',
          data: imageData, // Base64 encoded
        })
      );
    } catch (err) {
      console.error('Send image error:', err);
      setError('Failed to send image');
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    isConnecting,
    messages,
    error,
    connect,
    disconnect,
    sendText,
    sendAudio,
    sendImage,
    clearMessages,
  };
};
