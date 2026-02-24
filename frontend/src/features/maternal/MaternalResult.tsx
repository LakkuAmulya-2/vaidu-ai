interface MaternalResultProps {
  response: string;
}

const MaternalResult = ({ response }: MaternalResultProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">గర్భిణీ ఆరోగ్య సలహా</h3>
      <div className="bg-pink-50 rounded-lg p-4 whitespace-pre-wrap">
        {response}
      </div>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>ఉచిత ప్రభుత్వ సేవలు:</strong><br />
          • JSY: ప్రసవానికి నగదు సహాయం<br />
          • JSSK: ఉచిత డెలివరీ, C-section, మందులు<br />
          • PMSMA: ప్రతి నెల 9వ తేదీన ఉచిత చెక్-అప్<br />
          📞 ASHA వర్కర్ లేదా PHC సంప్రదించండి
        </p>
      </div>
    </div>
  );
};

export default MaternalResult;
