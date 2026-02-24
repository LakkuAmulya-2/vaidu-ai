import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import Input from '@/components/Input';

interface ChildHealthFormProps {
  onSubmit: (data: { query: string; age_months: number; weight_kg: number }) => void;
  isLoading: boolean;
}

const ChildHealthForm = ({ onSubmit, isLoading }: ChildHealthFormProps) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [ageMonths, setAgeMonths] = useState<number>(0);
  const [weightKg, setWeightKg] = useState<number>(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ query, age_months: ageMonths, weight_kg: weightKg });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('child.query')} *
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          className="input-field"
          placeholder={t('child.queryPlaceholder')}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('child.ageMonths')}
        </label>
        <Input
          type="number"
          value={ageMonths || ''}
          onChange={(e) => setAgeMonths(parseInt(e.target.value) || 0)}
          min={0}
          max={240}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('child.weightKg')}
        </label>
        <Input
          type="number"
          step="0.1"
          value={weightKg || ''}
          onChange={(e) => setWeightKg(parseFloat(e.target.value) || 0)}
          min={0}
          max={100}
        />
      </div>

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!query.trim()}
        fullWidth
      >
        {t('child.submit')}
      </Button>
    </form>
  );
};

export default ChildHealthForm;