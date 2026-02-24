import { useTranslation } from 'react-i18next';
import { useVerifyDoctor } from './useVerifyDoctor';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorDisplay from '@/components/ErrorDisplay';

interface VerifyDoctorResultProps {
  params: { name?: string; reg?: string };
  onReset: () => void;
}

const VerifyDoctorResult = ({ params, onReset }: VerifyDoctorResultProps) => {
  const { t } = useTranslation();
  const { data, isLoading, error } = useVerifyDoctor(params);

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorDisplay
        message={error.response || t('common.error')}
        onRetry={onReset}
      />
    );
  }

  if (!data) return null;

  const getAlertColor = (alert: string) => {
    switch (alert) {
      case 'GREEN':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'RED':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'YELLOW':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">ధృవీకరణ ఫలితం</h3>
      
      <div className={`rounded-lg border p-4 ${getAlertColor(data.alert || 'YELLOW')}`}>
        <div className="whitespace-pre-wrap">{data.response}</div>
      </div>

      {data.verified === false && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">
            <strong>⚠️ హెచ్చరిక:</strong> ఈ వ్యక్తి NMC డేటాబేస్‌లో కనిపించలేదు. 
            చట్టవిరుద్ధంగా ప్రాక్టీస్ చేస్తూ ఉండవచ్చు. 
            దయచేసి నమోదు చేసుకున్న ప్రభుత్వ PHC ను సందర్శించండి.
          </p>
        </div>
      )}

      <button
        onClick={onReset}
        className="btn-secondary w-full"
      >
        {t('verify.newSearch')}
      </button>
    </div>
  );
};

export default VerifyDoctorResult;
