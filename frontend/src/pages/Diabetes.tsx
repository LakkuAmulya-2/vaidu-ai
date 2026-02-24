import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import DiabetesForm from '@/features/diabetes/DiabetesForm';
import DiabetesResult from '@/features/diabetes/DiabetesResult';
import { useDiabetes } from '@/features/diabetes/useDiabetes';
import ErrorDisplay from '@/components/ErrorDisplay';

const Diabetes = () => {
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<any>(null);
  const { mutate, isPending, error } = useDiabetes();

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
      <h1 className="text-3xl font-bold mb-6">{t('diabetes.title')}</h1>
      <Card>
        {!result ? (
          <DiabetesForm onSubmit={handleSubmit} isLoading={isPending} />
        ) : (
          <div className="space-y-6">
            <DiabetesResult 
              response={result.response} 
              severity={result.severity}
              amie_state={result.amie_state}
            />
            <button
              onClick={() => setResult(null)}
              className="btn-secondary w-full"
            >
              {t('common.newQuery')}
            </button>
          </div>
        )}
        {error && <ErrorDisplay message={error.response || t('common.error')} onRetry={() => setResult(null)} />}
      </Card>
    </div>
  );
};

export default Diabetes;