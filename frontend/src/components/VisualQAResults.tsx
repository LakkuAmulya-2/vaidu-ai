import { useTranslation } from 'react-i18next';
import SpeakerButton from './SpeakerButton';

interface VisualQAResult {
  title?: string;
  snippet?: string;
  url?: string;
}

interface VisualQAResultsProps {
  results: VisualQAResult[];
  summary: string;
  count: number;
  searchAvailable: boolean;
}

const VisualQAResults = ({
  results,
  summary,
  count,
  searchAvailable,
}: VisualQAResultsProps) => {
  const { i18n } = useTranslation();

  if (!searchAvailable) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          {i18n.language === 'te' &&
            '⚠️ విజువల్ సెర్చ్ ప్రస్తుతం అందుబాటులో లేదు. దయచేసి వైద్యుడిని సంప్రదించండి.'}
          {i18n.language === 'hi' &&
            '⚠️ विज़ुअल सर्च वर्तमान में उपलब्ध नहीं है। कृपया डॉक्टर से परामर्श करें।'}
          {i18n.language === 'en' &&
            '⚠️ Visual search currently unavailable. Please consult a doctor.'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 mt-4">
      <div className="flex items-center justify-between">
        <h4 className="text-md font-semibold">
          {i18n.language === 'te' && `సారూప్య కేసులు (${count})`}
          {i18n.language === 'hi' && `समान मामले (${count})`}
          {i18n.language === 'en' && `Similar Cases (${count})`}
        </h4>
        <SpeakerButton text={summary} lang={i18n.language} />
      </div>

      {/* Summary */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <p className="text-sm text-purple-900 whitespace-pre-wrap">{summary}</p>
      </div>

      {/* Individual Results */}
      {results && results.length > 0 && (
        <div className="space-y-3">
          <h5 className="text-sm font-semibold text-gray-700">
            {i18n.language === 'te' && 'వివరాలు:'}
            {i18n.language === 'hi' && 'विवरण:'}
            {i18n.language === 'en' && 'Details:'}
          </h5>
          {results.map((result, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow"
            >
              {result.title && (
                <h6 className="font-medium text-gray-900 mb-1">
                  {index + 1}. {result.title}
                </h6>
              )}
              {result.snippet && (
                <p className="text-sm text-gray-700 mb-2">{result.snippet}</p>
              )}
              {result.url && (
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:underline"
                >
                  {i18n.language === 'te' && 'మరింత చదవండి →'}
                  {i18n.language === 'hi' && 'और पढ़ें →'}
                  {i18n.language === 'en' && 'Read more →'}
                </a>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-3">
        <p className="text-xs text-red-800">
          {i18n.language === 'te' &&
            '⚠️ ఇది AI-ఆధారిత సెర్చ్ మాత్రమే. ఖచ్చితమైన రోగ నిర్ధారణ కోసం వైద్యుడిని తప్పనిసరిగా సంప్రదించండి.'}
          {i18n.language === 'hi' &&
            '⚠️ यह केवल AI-आधारित खोज है। सटीक निदान के लिए डॉक्टर से अवश्य परामर्श करें।'}
          {i18n.language === 'en' &&
            '⚠️ This is AI-assisted search only. Always consult healthcare professionals for accurate diagnosis.'}
        </p>
      </div>
    </div>
  );
};

export default VisualQAResults;
