import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import InfectiousForm from '@/features/infectious/InfectiousForm';
import InfectiousResult from '@/features/infectious/InfectiousResult';
import { useInfectious } from '@/features/infectious/useInfectious';
import ErrorDisplay from '@/components/ErrorDisplay';

const Infectious = () => {
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<any>(null);
  const { mutate, isPending, error } = useInfectious();

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
      <h1 className="text-3xl font-bold mb-6">{t('infectious.title')}</h1>
      <Card>
        {!result ? (
          <InfectiousForm onSubmit={handleSubmit} isLoading={isPending} />
        ) : (
          <div className="space-y-6">
            <InfectiousResult response={result.response} />
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

export default Infectious;