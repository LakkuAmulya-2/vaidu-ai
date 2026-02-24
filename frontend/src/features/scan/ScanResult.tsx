interface ScanResultProps {
  response: string;
  scanType: string;
}

const ScanResult = ({ response, scanType }: ScanResultProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">స్కాన్ విశ్లేషణ - {scanType.toUpperCase()}</h3>
      <div className="bg-purple-50 rounded-lg p-4 whitespace-pre-wrap">
        {response}
      </div>
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-sm text-red-800">
          <strong>⚠️ హెచ్చరిక:</strong> ఇది AI అంచనా మాత్రమే. 
          ఖచ్చితమైన రోగ నిర్ధారణ కోసం రేడియాలజిస్ట్ లేదా స్పెషలిస్ట్ డాక్టర్‌ను తప్పనిసరిగా సంప్రదించండి.
        </p>
      </div>
    </div>
  );
};

export default ScanResult;
