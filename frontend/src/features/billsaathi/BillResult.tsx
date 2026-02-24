import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import Button from '@/components/Button';

interface BillResultProps {
  result: any;
  onGenerateDispute: () => void;
  onCheckInsurance: () => void;
}

const BillResult = ({ result, onGenerateDispute, onCheckInsurance }: BillResultProps) => {
  const { t } = useTranslation();

  if (!result || !result.data) {
    return null;
  }

  const { bill_data, overcharges, medicine_comparisons, necessity_results, summary, total_potential_savings } = result.data;

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      <Card>
        <h3 className="text-lg font-semibold mb-3">{t('billsaathi.summary')}</h3>
        <div className="prose prose-sm max-w-none">
          <p className="whitespace-pre-wrap">{summary}</p>
        </div>
        
        {total_potential_savings > 0 && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
            <p className="text-green-800 font-semibold">
              {t('billsaathi.potentialSavings')}: ₹{total_potential_savings.toFixed(2)}
            </p>
          </div>
        )}

        {result.confidence_score && (
          <div className="mt-2 text-sm text-gray-600">
            {t('billsaathi.confidenceScore')}: {(result.confidence_score * 100).toFixed(0)}%
          </div>
        )}
      </Card>

      {/* Bill Details */}
      <Card>
        <h3 className="text-lg font-semibold mb-3">{t('billsaathi.billDetails')}</h3>
        <div className="space-y-2 text-sm">
          <p><span className="font-medium">{t('billsaathi.hospital')}:</span> {bill_data.hospital_name}</p>
          <p><span className="font-medium">{t('billsaathi.billNumber')}:</span> {bill_data.bill_number}</p>
          <p><span className="font-medium">{t('billsaathi.billDate')}:</span> {bill_data.bill_date}</p>
          <p><span className="font-medium">{t('billsaathi.totalAmount')}:</span> ₹{bill_data.total}</p>
        </div>
      </Card>

      {/* Overcharges */}
      {overcharges && overcharges.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold mb-3 text-red-600">
            {t('billsaathi.overchargesFound')} ({overcharges.length})
          </h3>
          <div className="space-y-3">
            {overcharges.map((item: any, index: number) => (
              <div key={index} className="p-3 bg-red-50 border border-red-200 rounded">
                <p className="font-medium">{item.item_name}</p>
                <div className="text-sm mt-1 space-y-1">
                  <p>{t('billsaathi.charged')}: ₹{item.charged_price}</p>
                  <p>{t('billsaathi.cghsRate')}: ₹{item.cghs_rate}</p>
                  <p className="text-red-600 font-semibold">
                    {t('billsaathi.overcharge')}: ₹{item.overcharge_amount.toFixed(2)} ({item.overcharge_percentage.toFixed(1)}%)
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Medicine Comparisons */}
      {medicine_comparisons && medicine_comparisons.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold mb-3 text-blue-600">
            {t('billsaathi.medicineAlternatives')} ({medicine_comparisons.length})
          </h3>
          <div className="space-y-3">
            {medicine_comparisons.map((item: any, index: number) => (
              <div key={index} className="p-3 bg-blue-50 border border-blue-200 rounded">
                <p className="font-medium">{item.brand_name} → {item.generic_name}</p>
                <div className="text-sm mt-1 space-y-1">
                  <p>{t('billsaathi.brandPrice')}: ₹{item.charged_price} × {item.quantity}</p>
                  <p>{t('billsaathi.genericPrice')}: ₹{item.nppa_rate} × {item.quantity}</p>
                  <p className="text-green-600 font-semibold">
                    {t('billsaathi.savings')}: ₹{item.potential_savings.toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Medical Necessity */}
      {necessity_results && necessity_results.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold mb-3">{t('billsaathi.medicalNecessity')}</h3>
          <div className="space-y-3">
            {necessity_results.map((item: any, index: number) => (
              <div key={index} className={`p-3 border rounded ${
                item.necessity_level === 'unnecessary' ? 'bg-red-50 border-red-200' :
                item.necessity_level === 'optional' ? 'bg-yellow-50 border-yellow-200' :
                'bg-green-50 border-green-200'
              }`}>
                <p className="font-medium">{item.procedure_name}</p>
                <p className="text-sm mt-1">
                  <span className="font-medium">{t('billsaathi.necessity')}:</span> {item.necessity_level}
                </p>
                <p className="text-sm mt-1">{item.explanation}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        {overcharges && overcharges.length > 0 && (
          <Button onClick={onGenerateDispute} variant="secondary">
            {t('billsaathi.generateDisputeLetter')}
          </Button>
        )}
        <Button onClick={onCheckInsurance} variant="secondary">
          {t('billsaathi.checkInsurance')}
        </Button>
      </div>

      {/* Disclaimer */}
      {bill_data.disclaimer && (
        <div className="text-xs text-gray-600 p-3 bg-gray-50 rounded">
          {bill_data.disclaimer}
        </div>
      )}
    </div>
  );
};

export default BillResult;
