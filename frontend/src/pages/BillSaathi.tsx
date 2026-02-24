import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Card from '@/components/Card';
import BillUpload from '@/features/billsaathi/BillUpload';
import BillResult from '@/features/billsaathi/BillResult';
import InsuranceNavigator from '@/features/billsaathi/InsuranceNavigator';
import DisputeLetter from '@/features/billsaathi/DisputeLetter';
import LiveConsultation from '@/features/billsaathi/LiveConsultation';

type Tab = 'analyze' | 'insurance' | 'dispute' | 'live';

const BillSaathi = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>('analyze');
  const [billResult, setBillResult] = useState<any>(null);

  const tabs = [
    { id: 'analyze' as Tab, label: t('billsaathi.analyzeBill') },
    { id: 'insurance' as Tab, label: t('billsaathi.insurance') },
    { id: 'dispute' as Tab, label: t('billsaathi.dispute') },
    { id: 'live' as Tab, label: t('billsaathi.liveHelp') },
  ];

  const handleAnalysisComplete = (result: any) => {
    setBillResult(result);
  };

  const handleGenerateDispute = () => {
    setActiveTab('dispute');
  };

  const handleCheckInsurance = () => {
    setActiveTab('insurance');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t('billsaathi.title')}
        </h1>
        <p className="text-gray-600">
          {t('billsaathi.subtitle')}
        </p>
      </div>

      {/* Tabs */}
      <div>
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px space-x-4 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 px-4 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'analyze' && (
          <>
            <Card>
              <BillUpload onAnalysisComplete={handleAnalysisComplete} />
            </Card>
            
            {billResult && (
              <BillResult
                result={billResult}
                onGenerateDispute={handleGenerateDispute}
                onCheckInsurance={handleCheckInsurance}
              />
            )}
          </>
        )}

        {activeTab === 'insurance' && (
          <InsuranceNavigator billData={billResult?.data?.bill_data} />
        )}

        {activeTab === 'dispute' && (
          <>
            {billResult?.data?.overcharges && billResult.data.overcharges.length > 0 ? (
              <DisputeLetter
                overcharges={billResult.data.overcharges}
                billData={billResult.data.bill_data}
              />
            ) : (
              <Card>
                <p className="text-center text-gray-600">
                  {t('billsaathi.noOvercharges')}
                </p>
              </Card>
            )}
          </>
        )}

        {activeTab === 'live' && (
          <LiveConsultation />
        )}
      </div>

      {/* Info Cards */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card>
          <h3 className="font-semibold mb-2">{t('billsaathi.howItWorks')}</h3>
          <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
            <li>{t('billsaathi.step1')}</li>
            <li>{t('billsaathi.step2')}</li>
            <li>{t('billsaathi.step3')}</li>
            <li>{t('billsaathi.step4')}</li>
          </ul>
        </Card>

        <Card>
          <h3 className="font-semibold mb-2">{t('billsaathi.yourRights')}</h3>
          <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
            <li>{t('billsaathi.right1')}</li>
            <li>{t('billsaathi.right2')}</li>
            <li>{t('billsaathi.right3')}</li>
            <li>{t('billsaathi.right4')}</li>
          </ul>
        </Card>
      </div>
    </div>
  );
};

export default BillSaathi;
