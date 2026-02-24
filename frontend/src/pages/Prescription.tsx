import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import PrescriptionUpload from '@/features/prescription/PrescriptionUpload';
import PrescriptionResult from '@/features/prescription/PrescriptionResult';
import { usePrescription } from '@/features/prescription/usePrescription';
import ErrorDisplay from '@/components/ErrorDisplay';

const Prescription = () => {
  const { t, i18n } = useTranslation();
  const [result, setResult] = useState<any>(null);
  const { mutate, isPending, error } = usePrescription();

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
      <h1 className="text-3xl font-bold mb-6">{t('nav.prescription')}</h1>
      
      <Card>
        {!result ? (
          <PrescriptionUpload onSubmit={handleSubmit} isLoading={isPending} />
        ) : (
          <div className="space-y-6">
            <PrescriptionResult response={result.response} />
            <button
              onClick={() => setResult(null)}
              className="btn-secondary w-full"
            >
              {t('common.newUpload')}
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

export default Prescription;
