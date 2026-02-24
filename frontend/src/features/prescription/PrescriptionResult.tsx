interface PrescriptionResultProps {
  response: string;
}

const PrescriptionResult = ({ response }: PrescriptionResultProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">ప్రిస్క్రిప్షన్ విశ్లేషణ</h3>
      <div className="bg-blue-50 rounded-lg p-4 whitespace-pre-wrap">
        {response}
      </div>
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>గమనిక:</strong> ఏదైనా సందేహం ఉంటే ఫార్మసిస్ట్ లేదా డాక్టర్‌ను సంప్రదించండి. 
          మందుల మోతాదు మార్చకండి.
        </p>
      </div>
    </div>
  );
};

export default PrescriptionResult;
