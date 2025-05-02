# Kleurplatenmaken.ai 🎨

Een webapplicatie waarmee gebruikers een foto kunnen uploaden en een kleurplaatversie kunnen genereren op basis van drie moeilijkheidsgraden.

## Features

- 📸 Foto uploaden
- 🎨 Drie moeilijkheidsgraden voor kleurplaten
- 🤖 AI-gestuurde conversie
- 📱 Responsive design
- 💾 Directe download van kleurplaten

## Tech Stack

- Frontend: Next.js 14 (React)
- Backend: Python FastAPI
- AI: OpenAI API
- Styling: Tailwind CSS
- Database: PostgreSQL

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- PostgreSQL
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kleurplatenmaken.ai.git
cd kleurplatenmaken.ai
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Install backend dependencies:
```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start the development servers:

Frontend:
```bash
cd frontend
npm run dev
```

Backend:
```bash
cd backend
uvicorn main:app --reload
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 