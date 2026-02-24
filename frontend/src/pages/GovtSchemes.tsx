import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import GovtSchemesForm from '@/features/govt-schemes/GovtSchemesForm';
import GovtSchemesResult from '@/features/govt-schemes/GovtSchemesResult';
import { useGovtSchemes } from '@/features/govt-schemes/useGovtSchemes';
import ErrorDisplay from '@/components/ErrorDisplay';

const GovtSchemes = () => {
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<any>(null);
  const { mutate, isPending, error } = useGovtSchemes();

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
      <h1 className="text-3xl font-bold mb-6">{t('nav.govtSchemes')}</h1>
      
      <Card title={t('govtSchemes.title')}>
        {!result ? (
          <GovtSchemesForm onSubmit={handleSubmit} isLoading={isPending} />
        ) : (
          <div className="space-y-6">
            <GovtSchemesResult response={result.response} />
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

export default GovtSchemes;