import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import Input from '@/components/Input';
import MicButton from '@/components/MicButton';

interface TriageFormProps {
  onSubmit: (data: {
    symptoms: string;
    age: number;
    is_pregnant: boolean;
  }) => void;
  isLoading: boolean;
}

const TriageForm = ({ onSubmit, isLoading }: TriageFormProps) => {
  const { t, i18n } = useTranslation();
  const [symptoms, setSymptoms] = useState('');
  const [age, setAge] = useState<number>(0);
  const [isPregnant, setIsPregnant] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ symptoms, age, is_pregnant: isPregnant });
  };

  const handleTranscription = (text: string) => {
    setSymptoms(prev => prev ? `${prev} ${text}` : text);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('triage.symptoms')} *
        </label>
        <div className="flex gap-2">
          <textarea
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            rows={4}
            className="input-field flex-1"
            placeholder={t('triage.symptomsPlaceholder')}
            required
          />
          <MicButton 
            onTranscription={handleTranscription} 
            lang={i18n.language}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('triage.age')}
        </label>
        <Input
          type="number"
          value={age || ''}
          onChange={(e) => setAge(parseInt(e.target.value) || 0)}
          min={0}
          max={120}
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="pregnant"
          checked={isPregnant}
          onChange={(e) => setIsPregnant(e.target.checked)}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <label htmlFor="pregnant" className="ml-2 block text-sm text-gray-700">
          {t('triage.isPregnant')}
        </label>
      </div>

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!symptoms.trim()}
        fullWidth
      >
        {t('triage.submit')}
      </Button>
    </form>
  );
};

export default TriageForm;