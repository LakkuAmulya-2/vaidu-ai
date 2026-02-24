import SeverityBadge from '@/components/SeverityBadge';
import SpeakerButton from '@/components/SpeakerButton';
import { useTranslation } from 'react-i18next';

interface TriageResultProps {
  response: string;
  severity: string;
}

const TriageResult = ({ response, severity }: TriageResultProps) => {
  const { i18n } = useTranslation();
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">ఫలితం</h3>
        <div className="flex items-center gap-2">
          <SeverityBadge severity={severity} />
          <SpeakerButton text={response} lang={i18n.language} />
        </div>
      </div>
      <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap">
        {response}
      </div>
      {severity === 'RED' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-semibold">
            🚨 అత్యవసరం! వెంటనే 108 కాల్ చేయండి.
          </p>
        </div>
      )}
    </div>
  );
};

export default TriageResult;