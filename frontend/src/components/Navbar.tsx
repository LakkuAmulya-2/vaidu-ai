import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const { t } = useTranslation();

  const navItems = [
    { path: '/', label: t('nav.home') },
    { path: '/triage', label: t('nav.triage') },
    { path: '/prescription', label: t('nav.prescription') },
    { path: '/diabetes', label: t('nav.diabetes') },
    { path: '/billsaathi', label: t('nav.billSaathi') },
    { path: '/about', label: t('nav.about') },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-primary-700 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold">VAIDU</span>
            <span className="text-sm bg-primary-500 px-2 py-1 rounded">🏥</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`hover:text-primary-200 transition-colors ${
                  isActive(item.path) ? 'font-semibold border-b-2 border-white' : ''
                }`}
              >
                {item.label}
              </Link>
            ))}
            <LanguageSelector />
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden focus:outline-none"
            aria-label="Toggle menu"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {isOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`block py-2 hover:text-primary-200 transition-colors ${
                  isActive(item.path) ? 'font-semibold' : ''
                }`}
                onClick={() => setIsOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <div className="py-2">
              <LanguageSelector />
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;