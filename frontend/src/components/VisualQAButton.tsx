import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from './Button';
import Input from './Input';
import LoadingSpinner from './LoadingSpinner';

interface VisualQAResult {
  success: boolean;
  results: Array<{
    title?: string;
    snippet?: string;
    url?: string;
  }>;
  count: number;
  summary: string;
  search_available: boolean;
}

interface VisualQAButtonProps {
  imageFile: File | null;
  onResults: (results: VisualQAResult) => void;
  disabled?: boolean;
}

const VisualQAButton = ({ imageFile, onResults, disabled }: VisualQAButtonProps) => {
  const { t, i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!imageFile || !query.trim()) {
      setError(t('Please enter a question'));
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      formData.append('query', query.trim());

      const apiUrl = import.meta.env.VITE_API_URL || '/api';
      const response = await fetch(`${apiUrl}/visual-qa`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        onResults(data);
        setIsOpen(false);
        setQuery('');
      } else {
        setError(data.message || t('Search failed. Please try again.'));
      }
    } catch (err) {
      console.error('Visual Q&A error:', err);
      setError(t('Unable to search. Please try again.'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const getPlaceholder = () => {
    if (i18n.language === 'te') {
      return 'ఈ స్కాన్ గురించి ప్రశ్న అడగండి...';
    } else if (i18n.language === 'hi') {
      return 'इस स्कैन के बारे में प्रश्न पूछें...';
    }
    return 'Ask a question about this scan...';
  };

  const getButtonText = () => {
    if (i18n.language === 'te') {
      return '🔍 ఈ స్కాన్ గురించి అడగండి';
    } else if (i18n.language === 'hi') {
      return '🔍 इस स्कैन के बारे में पूछें';
    }
    return '🔍 Ask about this scan';
  };

  return (
    <div className="space-y-3">
      <Button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled || !imageFile}
        variant="secondary"
        className="w-full"
      >
        {getButtonText()}
      </Button>

      {isOpen && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
          <div className="text-sm text-blue-800">
            {i18n.language === 'te' && (
              <>
                <strong>సారూప్య కేసులు వెతకండి:</strong>
                <br />
                ఉదాహరణ: "ఇలాంటి న్యుమోనియా కేసులు చూపించు", "ఈ ఫ్రాక్చర్ రకం ఏమిటి?"
              </>
            )}
            {i18n.language === 'hi' && (
              <>
                <strong>समान मामले खोजें:</strong>
                <br />
                उदाहरण: "ऐसे निमोनिया के मामले दिखाएं", "यह फ्रैक्चर किस प्रकार का है?"
              </>
            )}
            {i18n.language === 'en' && (
              <>
                <strong>Search similar cases:</strong>
                <br />
                Example: "Show similar pneumonia cases", "What type of fracture is this?"
              </>
            )}
          </div>

          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={getPlaceholder()}
            disabled={isLoading}
          />

          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
              {error}
            </div>
          )}

          <div className="flex gap-2">
            <Button
              onClick={handleSearch}
              disabled={isLoading || !query.trim()}
              className="flex-1"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span className="ml-2">
                    {i18n.language === 'te' && 'వెతుకుతోంది...'}
                    {i18n.language === 'hi' && 'खोज रहा है...'}
                    {i18n.language === 'en' && 'Searching...'}
                  </span>
                </>
              ) : (
                <>
                  {i18n.language === 'te' && 'వెతకండి'}
                  {i18n.language === 'hi' && 'खोजें'}
                  {i18n.language === 'en' && 'Search'}
                </>
              )}
            </Button>
            <Button
              onClick={() => {
                setIsOpen(false);
                setQuery('');
                setError(null);
              }}
              variant="secondary"
            >
              {i18n.language === 'te' && 'రద్దు'}
              {i18n.language === 'hi' && 'रद्द करें'}
              {i18n.language === 'en' && 'Cancel'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisualQAButton;
