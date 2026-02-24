import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const Home = () => {
  const { t } = useTranslation();

  const features = [
    { path: '/triage', icon: '🩺', title: t('home.triage'), desc: t('home.triageDesc') },
    { path: '/prescription', icon: '📋', title: t('home.prescription'), desc: t('home.prescriptionDesc') },
    { path: '/diabetes', icon: '💉', title: t('home.diabetes'), desc: t('home.diabetesDesc') },
    { path: '/billsaathi', icon: '💰', title: t('home.billsaathi') || 'BillSaathi', desc: t('home.billsaathiDesc') || 'Medical bill analysis and insurance help' },
    { path: '/scan', icon: '🔬', title: t('home.scan') || 'Scan Analysis', desc: t('home.scanDesc') || 'Analyze X-ray, CT, MRI scans' },
    { path: '/skin', icon: '🔍', title: t('home.skin') || 'Skin Analysis', desc: t('home.skinDesc') || 'Analyze skin conditions' },
    { path: '/mental-health', icon: '🧠', title: t('home.mental'), desc: t('home.mentalDesc') },
    { path: '/maternal', icon: '🤰', title: t('home.maternal'), desc: t('home.maternalDesc') },
    { path: '/child-health', icon: '👶', title: t('home.child'), desc: t('home.childDesc') },
    { path: '/infectious', icon: '🦠', title: t('home.infectious') || 'Infectious Diseases', desc: t('home.infectiousDesc') || 'Guidance for infectious diseases' },
    { path: '/govt-schemes', icon: '🏛️', title: t('home.govtSchemes'), desc: t('home.govtSchemesDesc') },
    { path: '/verify-doctor', icon: '✅', title: t('home.verify'), desc: t('home.verifyDesc') },
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12 bg-gradient-to-r from-primary-50 to-primary-100 rounded-2xl">
        <h1 className="text-4xl md:text-5xl font-bold text-primary-800 mb-4">
          VAIDU
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          {t('home.tagline')}
        </p>
        <div className="mt-8">
          <Link
            to="/triage"
            className="btn-primary inline-block text-lg px-8 py-3"
          >
            {t('home.start')} →
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section>
        <h2 className="text-3xl font-semibold text-center mb-8">
          {t('home.services')}
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <Link
              key={feature.path}
              to={feature.path}
              className="card hover:shadow-lg transition-shadow group"
            >
              <div className="text-4xl mb-3 group-hover:scale-110 transition-transform">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.desc}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Emergency Banner */}
      <section className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h3 className="text-lg font-semibold text-red-800">
              🚨 {t('home.emergency')}
            </h3>
            <p className="text-red-700">
              {t('home.emergencyDesc')}
            </p>
          </div>
          <div className="text-3xl font-bold text-red-800">108</div>
        </div>
      </section>
    </div>
  );
};

export default Home;