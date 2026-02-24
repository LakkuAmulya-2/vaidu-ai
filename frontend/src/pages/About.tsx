import Card from '@/components/Card';

const About = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <h1 className="text-4xl font-bold text-center mb-8">VAIDU గురించి</h1>

      <Card>
        <h2 className="text-2xl font-semibold mb-4">మా లక్ష్యం</h2>
        <p className="text-gray-700 leading-relaxed mb-4">
          VAIDU (Voice AI for Indian Diagnostics & Understanding) గ్రామీణ భారతదేశంలోని 
          700 మిలియన్ల మందికి ఆరోగ్య సంరక్షణ మార్గదర్శకత్వం అందించడానికి రూపొందించబడింది.
        </p>
        <p className="text-gray-700 mb-4">
          Using advanced AI models (Gemini, MedGemma, HeAR), we offer services like symptom triage, 
          prescription analysis, medical scan interpretation, diabetes management, mental health support, 
          and information about government health schemes.
        </p>
        <p className="text-gray-700 mb-4">
          All responses are generated with safety and privacy in mind – we never store personal data, 
          strip metadata from images, and include clear disclaimers. In emergencies, we always advise 
          calling 108 immediately.
        </p>
        <div className="bg-primary-50 p-4 rounded-lg mb-4">
          <h3 className="font-semibold text-primary-800 mb-2">Key Features:</h3>
          <ul className="list-disc list-inside space-y-1 text-gray-700">
            <li>8 Indian languages supported (Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi, English)</li>
            <li>Image analysis for prescriptions, X-rays, skin conditions</li>
            <li>Diabetes risk assessment with LangGraph workflow</li>
            <li>Doctor registration verification via NMC database</li>
            <li>Cough analysis for TB screening (HeAR model)</li>
            <li>Free, anonymous, and private</li>
          </ul>
        </div>
        <p className="text-sm text-gray-500">
          Version 1.0.0 | © 2026 VAIDU. All rights reserved.
        </p>
      </Card>
    </div>
  );
};

export default About;