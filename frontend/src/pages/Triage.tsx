import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import ErrorDisplay from '@/components/ErrorDisplay';
import TriageForm from '@/features/triage/TriageForm';
import TriageResult from '@/features/triage/TriageResult';
import { useTriage } from '@/features/triage/useTriage';

const Triage = () => {
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<any>(null);
  const { mutate, isPending, error } = useTriage();

  const handleSubmit = (data: any) => {
    mutate(
      { ...data, lang: i18n.language },
      {
        onSuccess: (data) => {
          setResult(data);
        },
      }
    );
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">{t('nav.triage')}</h1>
      
      <Card>
        {!result ? (
          <TriageForm onSubmit={handleSubmit} isLoading={isPending} />
        ) : (
          <div className="space-y-6">
            <TriageResult
              response={result.response}
              severity={result.severity}
            />
            <button
              onClick={() => setResult(null)}
              className="btn-secondary w-full"
            >
              {t('common.newQuery')}
            </button>
          </div>
        )}

        {error && (
          <ErrorDisplay
            message={error.response || t('common.error')}
            onRetry={() => setResult(null)}
          />
        )}
      </Card>
    </div>
  );
};

export default Triage;