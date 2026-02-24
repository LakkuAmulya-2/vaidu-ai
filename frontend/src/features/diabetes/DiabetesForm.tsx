import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import Input from '@/components/Input';
import FileUpload from '@/components/FileUpload';

interface DiabetesFormProps {
  onSubmit: (data: {
    query: string;
    age: number;
    check_type: string;
    file?: File;
  }) => void;
  isLoading: boolean;
}

const DiabetesForm = ({ onSubmit, isLoading }: DiabetesFormProps) => {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [age, setAge] = useState<number>(0);
  const [checkType, setCheckType] = useState('general');
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      query,
      age,
      check_type: checkType,
      ...(file && { file }),
    });
  };

  const handleFileChange = (selectedFile: File | null) => {
    setFile(selectedFile);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('diabetes.query')} *
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          className="input-field"
          placeholder={t('diabetes.queryPlaceholder')}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('diabetes.age')}
        </label>
        <Input
          type="number"
          value={age || ''}
          onChange={(e) => setAge(parseInt(e.target.value) || 0)}
          min={0}
          max={120}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('diabetes.checkType')}
        </label>
        <select
          value={checkType}
          onChange={(e) => setCheckType(e.target.value)}
          className="input-field"
        >
          <option value="general">{t('diabetes.checkTypes.general')}</option>
          <option value="risk">{t('diabetes.checkTypes.risk')}</option>
          <option value="retinopathy">{t('diabetes.checkTypes.retinopathy')}</option>
          <option value="foot">{t('diabetes.checkTypes.foot')}</option>
          <option value="diet">{t('diabetes.checkTypes.diet')}</option>
          <option value="full">{t('diabetes.checkTypes.full')}</option>
        </select>
      </div>

      {(checkType === 'retinopathy' || checkType === 'foot' || checkType === 'full') && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('diabetes.uploadImage')} {checkType === 'retinopathy' ? t('diabetes.retinalImage') : t('diabetes.footImage')}
          </label>
          <FileUpload
            onFileSelect={handleFileChange}
            accept="image/jpeg,image/png,image/jpg"
            maxSize={10}
          />
        </div>
      )}

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!query.trim()}
        fullWidth
      >
        {t('diabetes.submit')}
      </Button>
    </form>
  );
};

export default DiabetesForm;
