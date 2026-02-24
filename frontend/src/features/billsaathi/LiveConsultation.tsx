import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import Card from '@/components/Card';
import { useLiveConsultation } from '@/hooks/useLiveConsultation';

const LiveConsultation = () => {
  const { t } = useTranslation();
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef(`session-${Date.now()}`);

  const {
    isConnected,
    isConnecting,
    messages,
    error,
    connect,
    disconnect,
    sendText,
    clearMessages,
  } = useLiveConsultation(sessionId.current);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputText.trim() || !isConnected) {
      return;
    }

    sendText(inputText);
    setInputText('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getStatusText = () => {
    if (isConnected) return t('billsaathi.connected') || 'Connected';
    if (isConnecting) return t('billsaathi.connecting') || 'Connecting...';
    return t('billsaathi.disconnected') || 'Disconnected';
  };

  const getStatusColor = () => {
    if (isConnected) return 'bg-green-500';
    if (isConnecting) return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-3">
        {t('billsaathi.liveConsultation') || 'Live Consultation'}
      </h3>
      
      <div className="space-y-4">
        {/* Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor()}`} />
            <span className="text-sm font-medium">{getStatusText()}</span>
          </div>

          {!isConnected && !isConnecting ? (
            <Button onClick={connect} size="sm">
              {t('billsaathi.connect') || 'Connect'}
            </Button>
          ) : (
            <Button onClick={disconnect} size="sm" variant="secondary">
              {t('billsaathi.disconnect') || 'Disconnect'}
            </Button>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">⚠️ {error}</p>
          </div>
        )}

        {/* Messages */}
        <div className="border border-gray-200 rounded-lg p-4 h-96 overflow-y-auto bg-gray-50">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 text-sm mt-8">
              {t('billsaathi.noMessages') || 'No messages yet. Connect to start consultation.'}
            </div>
          ) : (
            <div className="space-y-3">
              {messages.map((msg, index) => {
                // Handle different message types
                if (msg.type === 'emergency') {
                  return (
                    <div key={index} className="bg-red-100 border-2 border-red-500 rounded-lg p-4">
                      <div className="font-bold text-red-900 mb-2">
                        🚨 {msg.message}
                      </div>
                      {msg.reason && (
                        <p className="text-sm text-red-800 mb-2">{msg.reason}</p>
                      )}
                      {msg.actions && msg.actions.length > 0 && (
                        <div className="mt-2 space-y-1">
                          {msg.actions.map((action: any, i: number) => (
                            <div key={i} className="text-sm text-red-900">
                              • {action.message}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                }

                if (msg.type === 'tool_call') {
                  return (
                    <div key={index} className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                      <p className="text-xs text-purple-700 font-medium mb-1">
                        🔧 Tool: {msg.tool}
                      </p>
                      {msg.result && (
                        <p className="text-sm text-purple-900">
                          {JSON.stringify(msg.result, null, 2)}
                        </p>
                      )}
                    </div>
                  );
                }

                if (msg.type === 'audio') {
                  return (
                    <div key={index} className="flex justify-start">
                      <div className="bg-white border border-gray-200 rounded-lg p-3 max-w-[80%]">
                        <audio controls src={msg.data} className="w-full" />
                      </div>
                    </div>
                  );
                }

                if (msg.type === 'text') {
                  return (
                    <div key={index} className="flex justify-start">
                      <div className="bg-white border border-gray-200 rounded-lg p-3 max-w-[80%]">
                        <p className="text-sm whitespace-pre-wrap">{msg.data}</p>
                      </div>
                    </div>
                  );
                }

                return null;
              })}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={t('billsaathi.typeMessage') || 'Type your message...'}
            disabled={!isConnected}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || !isConnected}
          >
            {t('billsaathi.send') || 'Send'}
          </Button>
        </div>

        <div className="text-xs text-gray-600 p-3 bg-yellow-50 rounded">
          {t('billsaathi.liveConsultDisclaimer') ||
            '⚠️ This is AI-assisted consultation. For emergencies, call 108 immediately.'}
        </div>
      </div>
    </Card>
  );
};

export default LiveConsultation;
