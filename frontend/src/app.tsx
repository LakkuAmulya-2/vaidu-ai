import { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LoadingSpinner from './components/LoadingSpinner';

// Lazy load pages for better performance
const Home = lazy(() => import('./pages/Home'));
const Triage = lazy(() => import('./pages/Triage'));
const Prescription = lazy(() => import('./pages/Prescription'));
const Scan = lazy(() => import('./pages/Scan'));
const Skin = lazy(() => import('./pages/Skin'));
const Diabetes = lazy(() => import('./pages/Diabetes'));
const VerifyDoctor = lazy(() => import('./pages/VerifyDoctor'));
const Maternal = lazy(() => import('./pages/Maternal'));
const MentalHealth = lazy(() => import('./pages/MentalHealth'));
const ChildHealth = lazy(() => import('./pages/ChildHealth'));
const Infectious = lazy(() => import('./pages/Infectious'));
const GovtSchemes = lazy(() => import('./pages/GovtSchemes'));
const BillSaathi = lazy(() => import('./pages/BillSaathi'));
const About = lazy(() => import('./pages/About'));

function App() {
  const { i18n } = useTranslation();

  useEffect(() => {
    // Set HTML lang attribute based on current language
    document.documentElement.lang = i18n.language;
  }, [i18n.language]);

  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow container mx-auto px-4 py-8">
          <Suspense fallback={<LoadingSpinner />}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/triage" element={<Triage />} />
              <Route path="/prescription" element={<Prescription />} />
              <Route path="/scan" element={<Scan />} />
              <Route path="/skin" element={<Skin />} />
              <Route path="/diabetes" element={<Diabetes />} />
              <Route path="/verify-doctor" element={<VerifyDoctor />} />
              <Route path="/maternal" element={<Maternal />} />
              <Route path="/mental-health" element={<MentalHealth />} />
              <Route path="/child-health" element={<ChildHealth />} />
              <Route path="/infectious" element={<Infectious />} />
              <Route path="/govt-schemes" element={<GovtSchemes />} />
              <Route path="/billsaathi" element={<BillSaathi />} />
              <Route path="/about" element={<About />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;