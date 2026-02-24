import { useState } from 'react';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';

interface MicButtonProps {
  onTranscription: (text: string) => void;
  lang: string;
  className?: string;
}

const MicButton = ({ onTranscription, lang, className = '' }: MicButtonProps) => {
  const { isRecording, isProcessing, startRecording, stopRecording } = useAudioRecorder();
  const [error, setError] = useState<string | null>(null);

  const handleClick = async () => {
    setError(null);

    if (isRecording) {
      try {
        const text = await stopRecording(lang);
        onTranscription(text);
      } catch (err) {
        setError('రికార్డింగ్ విఫలమైంది. మళ్లీ ప్రయత్నించండి.');
        console.error(err);
      }
    } else {
      try {
        await startRecording();
      } catch (err) {
        setError('మైక్రోఫోన్ యాక్సెస్ నిరాకరించబడింది.');
        console.error(err);
      }
    }
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={handleClick}
        disabled={isProcessing}
        className={`p-3 rounded-full transition-all ${
          isRecording
            ? 'bg-red-500 hover:bg-red-600 animate-pulse'
            : 'bg-primary-500 hover:bg-primary-600'
        } text-white disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
        title={isRecording ? 'రికార్డింగ్ ఆపండి' : 'మైక్రోఫోన్ ప్రారంభించండి'}
      >
        {isProcessing ? (
          <svg className="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        ) : isRecording ? (
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <rect x="6" y="6" width="8" height="8" rx="1" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
          </svg>
        )}
      </button>
      
      {error && (
        <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 bg-red-100 text-red-800 text-xs px-3 py-1 rounded whitespace-nowrap">
          {error}
        </div>
      )}
    </div>
  );
};

export default MicButton;
