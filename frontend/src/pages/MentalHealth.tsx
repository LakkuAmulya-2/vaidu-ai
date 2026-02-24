import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import MentalHealthForm from '@/features/mental/MentalHealthForm';
import MentalHealthResult from '@/features/mental/MentalHealthResult';
import { useMentalHealth } from '@/features/mental/useMentalHealth';
import ErrorDisplay from '@/components/ErrorDisplay';

const MentalHealth = () => {
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<any>(null);
  const { mutate, isPending, error } = useMentalHealth();

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
      <h1 className="text-3xl font-bold mb-6">{t('nav.mentalHealth')}</h1>
      
      <Card title={t('mental.title')}>
        {!result ? (
          <MentalHealthForm onSubmit={handleSubmit} isLoading={isPending} />
        ) : (
          <div className="space-y-6">
            <MentalHealthResult response={result.response} />
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

export default MentalHealth;