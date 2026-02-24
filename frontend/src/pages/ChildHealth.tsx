import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import ChildHealthForm from '@/features/child/ChildHealthForm';
import ChildHealthResult from '@/features/child/ChildHealthResult';
import { useChildHealth } from '@/features/child/useChildHealth';
import ErrorDisplay from '@/components/ErrorDisplay';

const ChildHealth = () => {
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<any>(null);
  const { mutate, isPending, error } = useChildHealth();

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
      <h1 className="text-3xl font-bold mb-6">{t('child.title')}</h1>
      <Card>
        {!result ? (
          <ChildHealthForm onSubmit={handleSubmit} isLoading={isPending} />
        ) : (
          <div className="space-y-6">
            <ChildHealthResult response={result.response} />
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

export default ChildHealth;