interface GovtSchemesResultProps {
  response: string;
}

const GovtSchemesResult = ({ response }: GovtSchemesResultProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">ప్రభుత్వ పథకాల సమాచారం</h3>
      <div className="bg-green-50 rounded-lg p-4 whitespace-pre-wrap">
        {response}
      </div>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>మరింత సమాచారం కోసం:</strong><br />
          📞 హెల్ప్‌లైన్: 14555 (PM-JAY)<br />
          🌐 వెబ్‌సైట్: pmjay.gov.in<br />
          🏥 సమీప PHC లేదా ASHA వర్కర్‌ను సంప్రదించండి
        </p>
      </div>
    </div>
  );
};

export default GovtSchemesResult;
