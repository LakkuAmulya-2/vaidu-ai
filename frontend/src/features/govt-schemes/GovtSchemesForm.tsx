import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';

interface GovtSchemesFormProps {
  onSubmit: (data: { query: string }) => void;
  isLoading: boolean;
}

const GovtSchemesForm = ({ onSubmit, isLoading }: GovtSchemesFormProps) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ query });
  };

  const suggestions = [
    'PM-JAY (Ayushman Bharat)',
    'JSY (Janani Suraksha Yojana)',
    'JSSK (Janani Shishu Suraksha Karyakram)',
    'PMSMA (Pradhan Mantri Surakshit Matritva Abhiyan)',
    'RBSK (Rashtriya Bal Swasthya Karyakram)',
    'NMHP (National Mental Health Programme)',
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('govtSchemes.query')} *
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          className="input-field"
          placeholder={t('govtSchemes.placeholder')}
          required
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm font-medium text-blue-900 mb-2">
          {t('govtSchemes.suggestions')}:
        </p>
        <div className="flex flex-wrap gap-2">
          {suggestions.map((scheme) => (
            <button
              key={scheme}
              type="button"
              onClick={() => setQuery(scheme)}
              className="text-xs px-3 py-1 bg-white border border-blue-300 rounded-full hover:bg-blue-100 transition-colors"
            >
              {scheme}
            </button>
          ))}
        </div>
      </div>

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!query.trim()}
        fullWidth
      >
        {t('govtSchemes.submit')}
      </Button>
    </form>
  );
};

export default GovtSchemesForm;
