# VAIDU - AI Medical Assistant for Rural India 🏥

AI-powered healthcare platform providing medical guidance in Telugu, Hindi, and English for rural communities.

## 🌟 Features

### Core Medical Services
- **Symptom Triage** - AI-powered symptom assessment with severity classification
- **Prescription Analysis** - Analyze medical prescriptions and explain medicines
- **Medical Scan Analysis** - X-ray, CT, MRI interpretation
- **Skin Condition Analysis** - Dermatological assessment
- **Diabetes Management** - Comprehensive diabetes care guidance

### Specialized Services
- **BillSaathi** - Medical bill verification against CGHS rates
  - Overcharge detection
  - Insurance claim assistance
  - Dispute letter generation
  - Consumer forum guidance
- **AMIE Diagnostic** - Interactive diagnostic conversations
- **Live Consultation** - Real-time medical guidance
- **Maternal Health** - Pregnancy and maternal care guidance
- **Mental Health** - Mental wellness support
- **Child Health** - Pediatric care guidance
- **Infectious Diseases** - Disease prevention and management

### Multilingual Support
- Telugu (తెలుగు)
- Hindi (हिंदी)
- English
- Voice input/output support

## 🏗️ Architecture

### Frontend
- **React** with TypeScript
- **Vite** for fast development
- **TailwindCSS** for styling
- **React Query** for data fetching
- **i18next** for internationalization

### Backend
- **FastAPI** (Python)
- **Google Cloud Vertex AI** - MedGemma models
- **Gemini API** - Fallback for text/image processing
- **Google Maps API** - Location services

### AI Models
- **MedGemma 4B/27B** - Medical-specific language models
- **MedASR** - Medical speech recognition
- **HeAR** - Health acoustic representations
- **Gemini 1.5 Flash** - Fallback for general tasks

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud account with Vertex AI enabled
- Gemini API key (free from https://aistudio.google.com/app/apikey)

### Backend Setup

1. **Clone and navigate:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run server:**
   ```bash
   python main.py
   ```

   Server runs at: http://localhost:8000

### Frontend Setup

1. **Navigate and install:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

   App runs at: http://localhost:3000

## 🔧 Configuration

### Backend Environment Variables

```env
# Google Cloud Project
GOOGLE_CLOUD_PROJECT=your-project-id

# MedGemma Endpoints
MEDGEMMA_4B_ENDPOINT=your-endpoint-id
MEDGEMMA_4B_REGION=europe-west4
MEDGEMMA_27B_ENDPOINT=your-endpoint-id
MEDGEMMA_27B_REGION=europe-west4

# Audio Models
MEDASR_ENDPOINT=your-endpoint-id
MEDASR_REGION=asia-east1
HEAR_ENDPOINT=your-endpoint-id
HEAR_REGION=asia-east1

# Gemini API (Free alternative)
GEMINI_API_KEY=your-api-key

# Google Maps
GOOGLE_MAPS_API_KEY=your-api-key

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

### Getting API Keys

1. **Gemini API Key (FREE):**
   - Visit: https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy and add to `.env`

2. **Google Cloud Setup:**
   - Enable Vertex AI API
   - Deploy MedGemma endpoints
   - See `BILLING_SETUP_GUIDE.md` for details

3. **Google Maps API:**
   - Visit: https://console.cloud.google.com/apis/credentials
   - Create API key
   - Enable Maps JavaScript API

## 📚 Documentation

- [Backend Setup Guide](BACKEND_SETUP.md)
- [Billing Setup Guide](BILLING_SETUP_GUIDE.md)
- [BillSaathi Implementation](BILLSAATHI_IMPLEMENTATION.md)
- [Testing Guide](TESTING_GUIDE.md)
- [FastAPI Docs Guide](FASTAPI_DOCS_GUIDE.md)

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔒 Security Features

- Input sanitization and validation
- PII scrubbing for sensitive data
- Rate limiting (10 requests/minute)
- CORS protection
- Response validation
- Error handling with self-healing

## 🌍 Deployment

### Production Checklist
- [ ] Enable Google Cloud billing
- [ ] Set up budget alerts
- [ ] Configure production CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Enable monitoring and logging
- [ ] Set up backup strategy
- [ ] Configure CDN for frontend
- [ ] Set up CI/CD pipeline

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

[Add your license here]

## 👥 Team

VAIDU - AI Medical Assistant for Rural India

## 🙏 Acknowledgments

- Google Cloud for Vertex AI and MedGemma models
- FastAPI and React communities
- Open source contributors

## 📞 Support

For issues and questions:
- GitHub Issues: [Your repo URL]
- Email: [Your email]

## 🚨 Disclaimer

⚠️ **IMPORTANT:** This is an AI-powered medical guidance tool, NOT a replacement for professional medical advice. Always consult qualified healthcare professionals for diagnosis and treatment. In emergencies, call 108 immediately.

---

Made with ❤️ for rural India
