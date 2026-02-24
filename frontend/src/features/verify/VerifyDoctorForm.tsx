import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import Input from '@/components/Input';

interface VerifyDoctorFormProps {
  onSearch: (params: { name?: string; reg?: string }) => void;
}

const VerifyDoctorForm = ({ onSearch }: VerifyDoctorFormProps) => {
  const { t } = useTranslation();
  const [name, setName] = useState('');
  const [reg, setReg] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim() || reg.trim()) {
      onSearch({
        ...(name.trim() && { name: name.trim() }),
        ...(reg.trim() && { reg: reg.trim() }),
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <p className="text-sm text-blue-800">
          <strong>డాక్టర్ నమోదు ధృవీకరణ:</strong> NMC (National Medical Commission) డేటాబేస్‌లో 
          డాక్టర్ నమోదు చేసుకున్నారో లేదో తనిఖీ చేయండి.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('verify.doctorName')}
        </label>
        <Input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder={t('verify.namePlaceholder')}
        />
      </div>

      <div className="text-center text-sm text-gray-500">
        {t('verify.or')}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('verify.regNumber')}
        </label>
        <Input
          type="text"
          value={reg}
          onChange={(e) => setReg(e.target.value)}
          placeholder={t('verify.regPlaceholder')}
        />
      </div>

      <Button
        type="submit"
        disabled={!name.trim() && !reg.trim()}
        fullWidth
      >
        {t('verify.search')}
      </Button>
    </form>
  );
};

export default VerifyDoctorForm;
