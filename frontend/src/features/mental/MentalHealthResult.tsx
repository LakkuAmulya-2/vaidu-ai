interface MentalHealthResultProps {
  response: string;
}

const MentalHealthResult = ({ response }: MentalHealthResultProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">మానసిక ఆరోగ్య సలహా</h3>
      <div className="bg-blue-50 rounded-lg p-4 whitespace-pre-wrap">
        {response}
      </div>
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>సహాయక హెల్ప్‌లైన్లు:</strong><br />
          ఆస్రా: 91-22-27546669<br />
          వాండ్రేవాలా ఫౌండేషన్: 1860-2662-345
        </p>
      </div>
    </div>
  );
};

export default MentalHealthResult;