import SeverityBadge from '@/components/SeverityBadge';

interface SkinResultProps {
  response: string;
  severity?: string;
  area: string;
}

const SkinResult = ({ response, severity, area }: SkinResultProps) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          {area === 'skin' && 'చర్మ విశ్లేషణ'}
          {area === 'eye' && 'కంటి విశ్లేషణ'}
          {area === 'foot' && 'పాదాల విశ్లేషణ'}
        </h3>
        {severity && <SeverityBadge severity={severity} />}
      </div>
      <div className="bg-orange-50 rounded-lg p-4 whitespace-pre-wrap">
        {response}
      </div>
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>సలహా:</strong> ఇది AI అంచనా మాత్రమే. 
          {area === 'skin' && ' చర్మ వైద్యుడిని (డెర్మటాలజిస్ట్) సంప్రదించండి.'}
          {area === 'eye' && ' కంటి వైద్యుడిని (ఆప్తాల్మాలజిస్ట్) సంప్రదించండి.'}
          {area === 'foot' && ' మధుమేహ పాదాల సమస్యలు త్వరగా తీవ్రమవుతాయి. వెంటనే డాక్టర్‌ను సంప్రదించండి.'}
        </p>
      </div>
    </div>
  );
};

export default SkinResult;
