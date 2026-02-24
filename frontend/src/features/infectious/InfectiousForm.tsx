import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import Input from '@/components/Input';

interface InfectiousFormProps {
  onSubmit: (data: { symptoms: string; fever_days: number }) => void;
  isLoading: boolean;
}

const InfectiousForm = ({ onSubmit, isLoading }: InfectiousFormProps) => {
  const { t } = useTranslation();
  const [symptoms, setSymptoms] = useState('');
  const [feverDays, setFeverDays] = useState<number>(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ symptoms, fever_days: feverDays });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('infectious.symptoms')} *
        </label>
        <textarea
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          rows={3}
          className="input-field"
          placeholder={t('infectious.symptomsPlaceholder')}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('infectious.feverDays')}
        </label>
        <Input
          type="number"
          value={feverDays || ''}
          onChange={(e) => setFeverDays(parseInt(e.target.value) || 0)}
          min={0}
          max={30}
        />
      </div>

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!symptoms.trim()}
        fullWidth
      >
        {t('infectious.submit')}
      </Button>
    </form>
  );
};

export default InfectiousForm;