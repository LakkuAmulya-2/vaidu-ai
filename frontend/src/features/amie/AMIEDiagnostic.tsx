import { useTranslation } from 'react-i18next';
import SpeakerButton from '@/components/SpeakerButton';

interface DifferentialDiagnosis {
  condition: string;
  probability: number;
  reasoning: string;
}

interface AMIEDiagnosticProps {
  differentialDiagnoses?: DifferentialDiagnosis[];
  nextQuestions?: string[];
  redFlags?: string[];
  urgencyLevel?: string;
  currentAssessment?: string;
}

const AMIEDiagnostic = ({
  differentialDiagnoses = [],
  nextQuestions = [],
  redFlags = [],
  urgencyLevel = 'MEDIUM',
  currentAssessment = '',
}: AMIEDiagnosticProps) => {
  const { i18n } = useTranslation();

  if (
    !differentialDiagnoses.length &&
    !nextQuestions.length &&
    !redFlags.length &&
    !currentAssessment
  ) {
    return null;
  }

  const getUrgencyColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
      case 'HIGH':
        return 'bg-red-100 border-red-300 text-red-900';
      case 'MEDIUM':
        return 'bg-yellow-100 border-yellow-300 text-yellow-900';
      case 'LOW':
        return 'bg-green-100 border-green-300 text-green-900';
      default:
        return 'bg-gray-100 border-gray-300 text-gray-900';
    }
  };

  const getUrgencyLabel = (level: string) => {
    if (i18n.language === 'te') {
      switch (level) {
        case 'CRITICAL':
          return '🚨 అత్యవసరం';
        case 'HIGH':
          return '⚠️ అత్యంత ముఖ్యం';
        case 'MEDIUM':
          return '⚡ మధ్యస్థం';
        case 'LOW':
          return '✓ తక్కువ';
        default:
          return level;
      }
    } else if (i18n.language === 'hi') {
      switch (level) {
        case 'CRITICAL':
          return '🚨 आपातकालीन';
        case 'HIGH':
          return '⚠️ अत्यंत महत्वपूर्ण';
        case 'MEDIUM':
          return '⚡ मध्यम';
        case 'LOW':
          return '✓ कम';
        default:
          return level;
      }
    } else {
      return level;
    }
  };

  return (
    <div className="space-y-4 mt-6">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">
          {i18n.language === 'te' && 'AMIE రోగ నిర్ధారణ విశ్లేషణ'}
          {i18n.language === 'hi' && 'AMIE निदान विश्लेषण'}
          {i18n.language === 'en' && 'AMIE Diagnostic Analysis'}
        </h4>
        {currentAssessment && (
          <SpeakerButton text={currentAssessment} lang={i18n.language} />
        )}
      </div>

      {/* Urgency Level */}
      {urgencyLevel && (
        <div className={`border rounded-lg p-3 ${getUrgencyColor(urgencyLevel)}`}>
          <div className="font-semibold">
            {i18n.language === 'te' && 'అత్యవసర స్థాయి: '}
            {i18n.language === 'hi' && 'तात्कालिकता स्तर: '}
            {i18n.language === 'en' && 'Urgency Level: '}
            {getUrgencyLabel(urgencyLevel)}
          </div>
        </div>
      )}

      {/* Red Flags */}
      {redFlags.length > 0 && (
        <div className="bg-red-50 border border-red-300 rounded-lg p-4">
          <h5 className="font-semibold text-red-900 mb-2">
            {i18n.language === 'te' && '🚩 హెచ్చరిక సంకేతాలు:'}
            {i18n.language === 'hi' && '🚩 चेतावनी संकेत:'}
            {i18n.language === 'en' && '🚩 Warning Signs:'}
          </h5>
          <ul className="list-disc list-inside space-y-1 text-red-800">
            {redFlags.map((flag, index) => (
              <li key={index}>{flag}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Differential Diagnoses */}
      {differentialDiagnoses.length > 0 && (
        <div className="bg-blue-50 border border-blue-300 rounded-lg p-4">
          <h5 className="font-semibold text-blue-900 mb-3">
            {i18n.language === 'te' && '🔍 సంభావ్య రోగాలు:'}
            {i18n.language === 'hi' && '🔍 संभावित रोग:'}
            {i18n.language === 'en' && '🔍 Possible Conditions:'}
          </h5>
          <div className="space-y-3">
            {differentialDiagnoses.map((diagnosis, index) => (
              <div
                key={index}
                className="bg-white rounded-lg p-3 border border-blue-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">
                    {index + 1}. {diagnosis.condition}
                  </span>
                  <span className="text-sm font-semibold text-blue-700">
                    {Math.round(diagnosis.probability * 100)}%
                  </span>
                </div>
                {/* Probability Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${diagnosis.probability * 100}%` }}
                  />
                </div>
                {diagnosis.reasoning && (
                  <p className="text-sm text-gray-700">{diagnosis.reasoning}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next Questions */}
      {nextQuestions.length > 0 && (
        <div className="bg-purple-50 border border-purple-300 rounded-lg p-4">
          <h5 className="font-semibold text-purple-900 mb-2">
            {i18n.language === 'te' && '❓ మరిన్ని ప్రశ్నలు:'}
            {i18n.language === 'hi' && '❓ अधिक प्रश्न:'}
            {i18n.language === 'en' && '❓ Additional Questions:'}
          </h5>
          <p className="text-sm text-purple-800 mb-2">
            {i18n.language === 'te' &&
              'మరింత ఖచ్చితమైన నిర్ధారణ కోసం ఈ ప్రశ్నలకు సమాధానం ఇవ్వండి:'}
            {i18n.language === 'hi' &&
              'अधिक सटीक निदान के लिए इन प्रश्नों का उत्तर दें:'}
            {i18n.language === 'en' &&
              'Answer these questions for more accurate diagnosis:'}
          </p>
          <ul className="list-decimal list-inside space-y-1 text-purple-900">
            {nextQuestions.map((question, index) => (
              <li key={index}>{question}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Current Assessment */}
      {currentAssessment && (
        <div className="bg-gray-50 border border-gray-300 rounded-lg p-4">
          <h5 className="font-semibold text-gray-900 mb-2">
            {i18n.language === 'te' && '📋 ప్రస్తుత అంచనా:'}
            {i18n.language === 'hi' && '📋 वर्तमान मूल्यांकन:'}
            {i18n.language === 'en' && '📋 Current Assessment:'}
          </h5>
          <p className="text-gray-800 whitespace-pre-wrap">{currentAssessment}</p>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
        <p className="text-xs text-yellow-800">
          {i18n.language === 'te' &&
            '⚠️ ఇది AI-ఆధారిత ప్రాథమిక అంచనా మాత్రమే. ఖచ్చితమైన రోగ నిర్ధారణ కోసం వైద్యుడిని తప్పనిసరిగా సంప్రదించండి.'}
          {i18n.language === 'hi' &&
            '⚠️ यह केवल AI-आधारित प्रारंभिक मूल्यांकन है। सटीक निदान के लिए डॉक्टर से अवश्य परामर्श करें।'}
          {i18n.language === 'en' &&
            '⚠️ This is AI-assisted preliminary assessment only. Always consult a healthcare professional for accurate diagnosis.'}
        </p>
      </div>
    </div>
  );
};

export default AMIEDiagnostic;
