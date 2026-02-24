import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import FileUpload from '@/components/FileUpload';

interface PrescriptionUploadProps {
  onSubmit: (data: { file: File }) => void;
  isLoading: boolean;
}

const PrescriptionUpload = ({ onSubmit, isLoading }: PrescriptionUploadProps) => {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      onSubmit({ file });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('prescription.upload')} *
        </label>
        <FileUpload
          onFileSelect={setFile}
          accept="image/jpeg,image/png,image/jpg"
          maxSize={10}
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>చిట్కాలు:</strong><br />
          • స్పష్టమైన ఫోటో తీయండి<br />
          • మంచి వెలుతురు ఉండాలి<br />
          • అన్ని మందుల పేర్లు కనిపించాలి<br />
          • JPG లేదా PNG ఫార్మాట్ (గరిష్టం 10MB)
        </p>
      </div>

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!file}
        fullWidth
      >
        {t('prescription.analyze')}
      </Button>
    </form>
  );
};

export default PrescriptionUpload;
