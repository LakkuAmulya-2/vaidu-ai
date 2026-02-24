interface ChildHealthResultProps {
  response: string;
}

const ChildHealthResult = ({ response }: ChildHealthResultProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">పిల్లల ఆరోగ్య సలహా</h3>
      <div className="bg-blue-50 rounded-lg p-4 whitespace-pre-wrap">
        {response}
      </div>
    </div>
  );
};

export default ChildHealthResult;