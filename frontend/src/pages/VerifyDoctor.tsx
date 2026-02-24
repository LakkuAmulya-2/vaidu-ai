import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import VerifyDoctorForm from '@/features/verify/VerifyDoctorForm';
import VerifyDoctorResult from '@/features/verify/VerifyDoctorResult';

const VerifyDoctor = () => {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useState<{ name?: string; reg?: string } | null>(null);

  const handleSearch = (params: { name?: string; reg?: string }) => {
    setSearchParams(params);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">{t('nav.verify')}</h1>
      
      <Card>
        <VerifyDoctorForm onSearch={handleSearch} />
        
        {searchParams && (
          <div className="mt-6">
            <VerifyDoctorResult params={searchParams} onReset={() => setSearchParams(null)} />
          </div>
        )}
      </Card>
    </div>
  );
};

export default VerifyDoctor;
