import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import FileUpload from '@/components/FileUpload';

interface SkinUploadProps {
  onSubmit: (data: { file: File; area: string }) => void;
  isLoading: boolean;
}

const SkinUpload = ({ onSubmit, isLoading }: SkinUploadProps) => {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [area, setArea] = useState('skin');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      onSubmit({ file, area });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('skin.area')} *
        </label>
        <select
          value={area}
          onChange={(e) => setArea(e.target.value)}
          className="input-field"
        >
          <option value="skin">{t('skin.areas.skin')}</option>
          <option value="eye">{t('skin.areas.eye')}</option>
          <option value="foot">{t('skin.areas.foot')}</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('skin.upload')} *
        </label>
        <FileUpload
          onFileSelect={setFile}
          accept="image/jpeg,image/png,image/jpg"
          maxSize={10}
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>ఫోటో చిట్కాలు:</strong><br />
          • ప్రభావిత ప్రాంతం స్పష్టంగా కనిపించాలి<br />
          • మంచి వెలుతురు ఉండాలి<br />
          • దగ్గరగా తీయండి కానీ బ్లర్ కాకుండా<br />
          • పోలిక కోసం పక్కన రూలర్ లేదా నాణెం పెట్టవచ్చు
        </p>
      </div>

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!file}
        fullWidth
      >
        {t('skin.analyze')}
      </Button>
    </form>
  );
};

export default SkinUpload;
