interface InfectiousResultProps {
  response: string;
}

const InfectiousResult = ({ response }: InfectiousResultProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">అంటువ్యాధి సలహా</h3>
      <div className="bg-yellow-50 rounded-lg p-4 whitespace-pre-wrap">
        {response}
      </div>
    </div>
  );
};

export default InfectiousResult;