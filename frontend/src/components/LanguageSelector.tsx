import { useTranslation } from 'react-i18next';

const languages = [
  { code: 'te', name: 'తెలుగు' },
  { code: 'hi', name: 'हिन्दी' },
  { code: 'ta', name: 'தமிழ்' },
  { code: 'kn', name: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'മലയാളം' },
  { code: 'bn', name: 'বাংলা' },
  { code: 'mr', name: 'मराठी' },
  { code: 'en', name: 'English' },
];

const LanguageSelector = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <select
      value={i18n.language}
      onChange={(e) => changeLanguage(e.target.value)}
      className="bg-primary-600 text-white border border-primary-500 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-white"
      aria-label="Select language"
    >
      {languages.map((lang) => (
        <option key={lang.code} value={lang.code} className="bg-primary-700">
          {lang.name}
        </option>
      ))}
    </select>
  );
};

export default LanguageSelector;