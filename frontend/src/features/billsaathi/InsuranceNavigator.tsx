import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import FileUpload from '@/components/FileUpload';
import Input from '@/components/Input';
import Button from '@/components/Button';
import Card from '@/components/Card';
import { useInsuranceNavigate } from './useBillSaathi';

interface InsuranceNavigatorProps {
  billData?: any;
}

const InsuranceNavigator = ({ billData }: InsuranceNavigatorProps) => {
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.language;
  const [policyFile, setPolicyFile] = useState<File | null>(null);
  const [patientName, setPatientName] = useState('');
  const [diagnosis, setDiagnosis] = useState('');
  const [result, setResult] = useState<any>(null);

  const insuranceNavigate = useInsuranceNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!policyFile) {
      alert(t('billsaathi.pleaseUploadPolicy'));
      return;
    }

    if (!billData) {
      alert(t('billsaathi.billDataRequired'));
      return;
    }

    try {
      const response = await insuranceNavigate.mutateAsync({
        policy_file: policyFile,
        bill_data: JSON.stringify(billData),
        patient_name: patientName,
        diagnosis,
        lang: currentLanguage,
      });
      
      setResult(response.data);
    } catch (error) {
      console.error('Insurance navigation error:', error);
    }
  };

  return (
    <div className="space-y-4">
      {!result ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <Card>
            <h3 className="text-lg font-semibold mb-3">{t('billsaathi.insuranceNavigator')}</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  {t('billsaathi.uploadPolicy')}
                </label>
                <FileUpload
                  accept="image/*"
                  onChange={(file) => setPolicyFile(file)}
                  label={t('billsaathi.selectPolicyImage')}
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
                disabled={!policyFile || insuranceNavigate.isPending}
                isLoading={insuranceNavigate.isPending}
                fullWidth
              >
                {t('billsaathi.checkCoverage')}
              </Button>

              {insuranceNavigate.isError && (
                <div className="text-red-600 text-sm">
                  {t('billsaathi.insuranceError')}
                </div>
              )}
            </div>
          </Card>
        </form>
      ) : (
        <div className="space-y-4">
          {/* Policy Details */}
          <Card>
            <h3 className="text-lg font-semibold mb-3">{t('billsaathi.policyDetails')}</h3>
            <div className="space-y-2 text-sm">
              <p><span className="font-medium">{t('billsaathi.policyNumber')}:</span> {result.policy_details.policy_number}</p>
              <p><span className="font-medium">{t('billsaathi.insuranceCompany')}:</span> {result.policy_details.insurance_company}</p>
              <p><span className="font-medium">{t('billsaathi.sumInsured')}:</span> ₹{result.policy_details.sum_insured}</p>
            </div>
          </Card>

          {/* Coverage Analysis */}
          <Card>
            <h3 className="text-lg font-semibold mb-3">{t('billsaathi.coverageAnalysis')}</h3>
            <div className="space-y-3">
              <div className={`p-3 rounded ${
                result.coverage_analysis.overall_coverage === 'covered' ? 'bg-green-50' :
                result.coverage_analysis.overall_coverage === 'partially_covered' ? 'bg-yellow-50' :
                'bg-red-50'
              }`}>
                <p className="font-medium">{t('billsaathi.overallCoverage')}: {result.coverage_analysis.overall_coverage}</p>
                <p className="text-sm mt-1">{t('billsaathi.coveredAmount')}: ₹{result.coverage_analysis.covered_amount}</p>
                <p className="text-sm">{t('billsaathi.patientLiability')}: ₹{result.coverage_analysis.patient_liability}</p>
              </div>

              <div className="prose prose-sm max-w-none">
                <p>{result.coverage_analysis.coverage_summary}</p>
              </div>
            </div>
          </Card>

          {/* Claim Documents */}
          {result.claim_documents && (
            <Card>
              <h3 className="text-lg font-semibold mb-3">{t('billsaathi.claimDocuments')}</h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">{t('billsaathi.claimLetter')}</h4>
                  <div className="p-3 bg-gray-50 rounded text-sm whitespace-pre-wrap">
                    {result.claim_documents.claim_letter}
                  </div>
                </div>

                {result.claim_documents.document_checklist && result.claim_documents.document_checklist.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">{t('billsaathi.documentChecklist')}</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {result.claim_documents.document_checklist.map((doc: string, index: number) => (
                        <li key={index}>{doc}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </Card>
          )}

          <Button onClick={() => setResult(null)} variant="secondary">
            {t('billsaathi.checkAnother')}
          </Button>
        </div>
      )}
    </div>
  );
};

export default InsuranceNavigator;
