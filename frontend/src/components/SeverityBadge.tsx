interface SeverityBadgeProps {
  severity: 'GREEN' | 'YELLOW' | 'RED' | string;
}

const SeverityBadge = ({ severity }: SeverityBadgeProps) => {
  const getBadgeClasses = () => {
    switch (severity?.toUpperCase()) {
      case 'GREEN':
        return 'severity-badge severity-badge-green';
      case 'YELLOW':
        return 'severity-badge severity-badge-yellow';
      case 'RED':
        return 'severity-badge severity-badge-red';
      default:
        return 'severity-badge bg-gray-100 text-gray-800';
    }
  };

  const getLabel = () => {
    switch (severity?.toUpperCase()) {
      case 'GREEN':
        return 'తక్కువ ప్రమాదం';
      case 'YELLOW':
        return 'మధ్యస్థ ప్రమాదం';
      case 'RED':
        return 'అత్యవసరం';
      default:
        return severity || 'తెలియదు';
    }
  };

  return (
    <span className={getBadgeClasses()}>
      {getLabel()}
    </span>
  );
};

export default SeverityBadge;