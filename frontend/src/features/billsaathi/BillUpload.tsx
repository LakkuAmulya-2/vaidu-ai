import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import FileUpload from '@/components/FileUpload';
import Input from '@/components/Input';
import Button from '@/components/Button';
import { useBillAnalysis } from './useBillSaathi';

interface BillUploadProps {
  onAnalysisComplete: (result: any) => void;
}

const BillUpload = ({ onAnalysisComplete }: BillUploadProps) => {
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.language;
  const [file, setFile] = useState<File | null>(null);
  const [diagnosis, setDiagnosis] = useState('');
  const [patientName, setPatientName] = useState('');

  const billAnalysis = useBillAnalysis();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      alert(t('billsaathi.pleaseUploadBill'));
      return;
    }

    try {
      const result = await billAnalysis.mutateAsync({
        file,
        diagnosis,
        patient_name: patientName,
        lang: currentLanguage,
      });
      
      onAnalysisComplete(result);
    } catch (error) {
      console.error('Bill analysis error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">
          {t('billsaathi.uploadBill')}
        </label>
        <FileUpload
          accept="image/*"
          onFileSelect={(selectedFile) => setFile(selectedFile)}
          label={t('billsaathi.selectBillImage')}
        />
      </div>

      <Input
        label={t('billsaathi.patientName')}
        value={patientName}
        onChange={(e) => setPatientName(e.target.value)}
        placeholder={t('billsaathi.patientNamePlaceholder')}
      />

      <Input
        label={t('billsaathi.diagnosis')}
        value={diagnosis}
        onChange={(e) => setDiagnosis(e.target.value)}
        placeholder={t('billsaathi.diagnosisPlaceholder')}
      />

      <Button
        type="submit"
        disabled={!file || billAnalysis.isPending}
        isLoading={billAnalysis.isPending}
        fullWidth
      >
        {t('billsaathi.analyzeBill')}
      </Button>

      {billAnalysis.isError && (
        <div className="text-red-600 text-sm mt-2">
          {t('billsaathi.analysisError')}
        </div>
      )}
    </form>
  );
};

export default BillUpload;
