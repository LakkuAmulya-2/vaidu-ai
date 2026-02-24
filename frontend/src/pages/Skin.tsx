import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import SkinUpload from '@/features/skin/SkinUpload';
import SkinResult from '@/features/skin/SkinResult';
import { useSkin } from '@/features/skin/useSkin';
import ErrorDisplay from '@/components/ErrorDisplay';
import VisualQAButton from '@/components/VisualQAButton';
import VisualQAResults from '@/components/VisualQAResults';

const Skin = () => {
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<any>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [visualQAResults, setVisualQAResults] = useState<any>(null);
  const { mutate, isPending, error } = useSkin();

  const handleSubmit = (data: any) => {
    setUploadedFile(data.file);
    setVisualQAResults(null);
    
    mutate(
      { ...data, lang: i18n.language },
      {
        onSuccess: (data) => {
          setResult(data);
        },
      }
    );
  };

  const handleVisualQAResults = (qaResults: any) => {
    setVisualQAResults(qaResults);
  };

  const handleNewUpload = () => {
    setResult(null);
    setUploadedFile(null);
    setVisualQAResults(null);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">{t('nav.skin')}</h1>
      
      <Card>
        {!result ? (
          <SkinUpload onSubmit={handleSubmit} isLoading={isPending} />
        ) : (
          <div className="space-y-6">
            <SkinResult 
              response={result.response} 
              severity={result.severity}
              area={result.area || 'skin'}
            />
            
            {/* Visual Q&A Section */}
            <VisualQAButton
              imageFile={uploadedFile}
              onResults={handleVisualQAResults}
              disabled={isPending}
            />
            
            {visualQAResults && (
              <VisualQAResults
                results={visualQAResults.results || []}
                summary={visualQAResults.summary || ''}
                count={visualQAResults.count || 0}
                searchAvailable={visualQAResults.search_available !== false}
              />
            )}
            
            <button
              onClick={handleNewUpload}
              className="btn-secondary w-full"
            >
              {t('common.newUpload')}
            </button>
          </div>
        )}

        {error && (
          <ErrorDisplay
            message={error.response || t('common.error')}
            onRetry={handleNewUpload}
          />
        )}
      </Card>
    </div>
  );
};

export default Skin;
