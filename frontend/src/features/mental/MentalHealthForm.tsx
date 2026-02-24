import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';

interface MentalHealthFormProps {
  onSubmit: (data: { query: string }) => void;
  isLoading: boolean;
}

const MentalHealthForm = ({ onSubmit, isLoading }: MentalHealthFormProps) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ query });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('mental.describe')} *
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
          className="input-field"
          placeholder={t('mental.placeholder')}
          required
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          {t('mental.disclaimer')}
        </p>
      </div>

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!query.trim()}
        fullWidth
      >
        {t('mental.submit')}
      </Button>
    </form>
  );
};

export default MentalHealthForm;