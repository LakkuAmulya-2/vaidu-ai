import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import Input from '@/components/Input';

interface MaternalFormProps {
  onSubmit: (data: { query: string; week: number }) => void;
  isLoading: boolean;
}

const MaternalForm = ({ onSubmit, isLoading }: MaternalFormProps) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [week, setWeek] = useState<number>(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ query, week });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('maternal.query')} *
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          className="input-field"
          placeholder={t('maternal.queryPlaceholder')}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('maternal.week')}
        </label>
        <Input
          type="number"
          value={week || ''}
          onChange={(e) => setWeek(parseInt(e.target.value) || 0)}
          min={0}
          max={42}
          placeholder="0-42"
        />
      </div>

      <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
        <p className="text-sm text-pink-800">
          <strong>ప్రమాద సంకేతాలు:</strong> రక్తస్రావం, తీవ్రమైన నొప్పి, కంటి చూపు మార్పులు, 
          ముఖం వాపు, శిశువు కదలికలు లేకపోవడం - వెంటనే ఆసుపత్రికి వెళ్లండి.
        </p>
      </div>

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!query.trim()}
        fullWidth
      >
        {t('maternal.submit')}
      </Button>
    </form>
  );
};

export default MaternalForm;
