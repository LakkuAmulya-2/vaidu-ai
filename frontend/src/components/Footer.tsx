import { useTranslation } from 'react-i18next';

const Footer = () => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-800 text-white mt-auto">
      <div className="container mx-auto px-4 py-8">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">VAIDU</h3>
            <p className="text-gray-300 text-sm">
              {t('footer.description')}
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">{t('footer.quickLinks')}</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="/about" className="text-gray-300 hover:text-white transition-colors">
                  {t('nav.about')}
                </a>
              </li>
              <li>
                <a href="/privacy" className="text-gray-300 hover:text-white transition-colors">
                  {t('footer.privacy')}
                </a>
              </li>
              <li>
                <a href="/terms" className="text-gray-300 hover:text-white transition-colors">
                  {t('footer.terms')}
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">{t('footer.contact')}</h3>
            <p className="text-gray-300 text-sm">
              {t('footer.emergency')}: <span className="font-bold text-red-400">108</span>
            </p>
            <p className="text-gray-300 text-sm mt-2">
              {t('footer.helpline')}: 1800-XXX-XXXX
            </p>
          </div>
        </div>
        <div className="border-t border-gray-700 mt-8 pt-6 text-center text-sm text-gray-400">
          © {currentYear} VAIDU. {t('footer.rights')}
        </div>
      </div>
    </footer>
  );
};

export default Footer;