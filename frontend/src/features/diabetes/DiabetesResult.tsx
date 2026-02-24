import SeverityBadge from '@/components/SeverityBadge';
import SpeakerButton from '@/components/SpeakerButton';
import AMIEDiagnostic from '@/features/amie/AMIEDiagnostic';
import { useTranslation } from 'react-i18next';

interface DiabetesResultProps {
  response: string;
  severity?: string;
  amie_state?: {
    differential_diagnoses?: Array<{
      condition: string;
      probability: number;
      reasoning: string;
    }>;
    next_questions?: string[];
    red_flags?: string[];
    urgency_level?: string;
    current_assessment?: string;
  };
}

const DiabetesResult = ({ response, severity, amie_state }: DiabetesResultProps) => {
  const { i18n } = useTranslation();
  
  // Parse the markdown-style response
  const parseResponse = (text: string) => {
    // Split by double asterisks for bold sections
    const sections = text.split(/\*\*(.*?)\*\*/g);
    
    return sections.map((section, index) => {
      // Odd indices are the bold text
      if (index % 2 === 1) {
        return <strong key={index} className="font-semibold text-gray-900">{section}</strong>;
      }
      
      // Split by newlines and render
      const lines = section.split('\n').filter(line => line.trim());
      return lines.map((line, lineIndex) => {
        // Check if it's a bullet point
        if (line.trim().startsWith('-')) {
          return (
            <li key={`${index}-${lineIndex}`} className="ml-4">
              {line.trim().substring(1).trim()}
            </li>
          );
        }
        // Regular line
        return (
          <p key={`${index}-${lineIndex}`} className="mb-2">
            {line}
          </p>
        );
      });
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">మధుమేహం మార్గదర్శనం</h3>
        <div className="flex items-center gap-2">
          {severity && <SeverityBadge severity={severity} />}
          <SpeakerButton text={response} lang={i18n.language} />
        </div>
      </div>
      
      <div className="bg-blue-50 rounded-lg p-4">
        <div className="text-gray-800 space-y-2">
          {parseResponse(response)}
        </div>
      </div>

      {/* AMIE Diagnostic Section */}
      {amie_state && (
        <AMIEDiagnostic
          differentialDiagnoses={amie_state.differential_diagnoses}
          nextQuestions={amie_state.next_questions}
          redFlags={amie_state.red_flags}
          urgencyLevel={amie_state.urgency_level}
          currentAssessment={amie_state.current_assessment}
        />
      )}

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>⚠️ ముఖ్యమైనది:</strong> ఇది AI మార్గదర్శకత్వం మాత్రమే. 
          రక్త చక్కెర నియంత్రణ మరియు చికిత్స కోసం వైద్యుడిని తప్పనిసరిగా సంప్రదించండి.
        </p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <p className="text-sm text-green-800">
          <strong>ఉచిత సేవలు:</strong><br />
          • NPCDCS: ఉచిత మధుమేహ స్క్రీనింగ్<br />
          • PHC వద్ద ఉచిత రక్త పరీక్షలు<br />
          • ఉచిత మందులు అందుబాటులో ఉన్నాయి
        </p>
      </div>
    </div>
  );
};

export default DiabetesResult;
