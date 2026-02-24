import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Button from '@/components/Button';
import Card from '@/components/Card';
import { useDisputeLetter } from './useBillSaathi';

interface DisputeLetterProps {
  overcharges: any[];
  billData: any;
}

const DisputeLetter = ({ overcharges, billData }: DisputeLetterProps) => {
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.language;
  const [letter, setLetter] = useState<string>('');
  
  const disputeLetter = useDisputeLetter();

  const handleGenerate = async () => {
    try {
      const response = await disputeLetter.mutateAsync({
        overcharge_items: JSON.stringify(overcharges),
        hospital_name: billData.hospital_name || '',
        patient_name: billData.patient_name || '',
        bill_number: billData.bill_number || '',
        bill_date: billData.bill_date || '',
        lang: currentLanguage,
      });
      
      setLetter(response.letter);
    } catch (error) {
      console.error('Dispute letter generation error:', error);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(letter);
    alert(t('billsaathi.letterCopied'));
  };

  const handleDownload = () => {
    const blob = new Blob([letter], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dispute-letter-${billData.bill_number || 'bill'}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Card>
      <h3 className="text-lg font-semibold mb-3">{t('billsaathi.disputeLetter')}</h3>
      
      {!letter ? (
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            {t('billsaathi.disputeLetterDescription')}
          </p>
          
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-sm font-medium">{t('billsaathi.overchargesSummary')}:</p>
            <p className="text-sm mt-1">
              {t('billsaathi.totalOvercharge')}: ₹{overcharges.reduce((sum, item) => sum + item.overcharge_amount, 0).toFixed(2)}
            </p>
            <p className="text-sm">{t('billsaathi.itemsCount')}: {overcharges.length}</p>
          </div>

          <Button
            onClick={handleGenerate}
            disabled={disputeLetter.isPending}
            isLoading={disputeLetter.isPending}
            fullWidth
          >
            {t('billsaathi.generateLetter')}
          </Button>

          {disputeLetter.isError && (
            <div className="text-red-600 text-sm">
              {t('billsaathi.letterGenerationError')}
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="p-4 bg-gray-50 rounded border border-gray-200 max-h-96 overflow-y-auto">
            <pre className="whitespace-pre-wrap text-sm font-mono">{letter}</pre>
          </div>

          <div className="flex gap-3">
            <Button onClick={handleCopy} variant="secondary">
              {t('billsaathi.copyLetter')}
            </Button>
            <Button onClick={handleDownload} variant="secondary">
              {t('billsaathi.downloadLetter')}
            </Button>
            <Button onClick={() => setLetter('')} variant="secondary">
              {t('billsaathi.generateNew')}
            </Button>
          </div>

          <div className="text-xs text-gray-600 p-3 bg-blue-50 rounded">
            {t('billsaathi.letterDisclaimer')}
          </div>
        </div>
      )}
    </Card>
  );
};

export default DisputeLetter;
