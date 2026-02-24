import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import FileUpload from '@/components/FileUpload';

interface ScanUploadProps {
  onSubmit: (data: { file: File; scan_type: string }) => void;
  isLoading: boolean;
}

const ScanUpload = ({ onSubmit, isLoading }: ScanUploadProps) => {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [scanType, setScanType] = useState('xray');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      onSubmit({ file, scan_type: scanType });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('scan.type')} *
        </label>
        <select
          value={scanType}
          onChange={(e) => setScanType(e.target.value)}
          className="input-field"
        >
          <option value="xray">{t('scan.types.xray')}</option>
          <option value="ct">{t('scan.types.ct')}</option>
          <option value="mri">{t('scan.types.mri')}</option>
          <option value="lab">{t('scan.types.lab')}</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('scan.upload')} *
        </label>
        <FileUpload
          onFileSelect={setFile}
          accept="image/jpeg,image/png,image/jpg"
          maxSize={10}
        />
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>ముఖ్యమైనది:</strong> ఇది AI విశ్లేషణ మాత్రమే. 
          ఖచ్చితమైన నిర్ధారణ కోసం రేడియాలజిస్ట్ లేదా స్పెషలిస్ట్‌ను తప్పనిసరిగా సంప్రదించండి.
        </p>
      </div>

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!file}
        fullWidth
      >
        {t('scan.analyze')}
      </Button>
    </form>
  );
};

export default ScanUpload;
