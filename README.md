# Pehance

A modern web application with a Next.js frontend and Python FastAPI backend, designed to provide AI-powered enhancements and insights.

## 🚀 Features

- **Modern UI**: Built with Next.js and TypeScript
- **AI Integration**: Powered by Groq and OpenAI APIs
- **Real-time Analysis**: FastAPI backend for processing
- **Responsive Design**: Beautiful, modern interface
- **Theme Support**: Dark/light mode toggle

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Jest** - Testing
- **ESLint** - Code linting

### Backend
- **FastAPI** - Python web framework
- **Groq** - AI model integration
- **OpenAI** - Additional AI capabilities
- **Pydantic** - Data validation

## 📁 Project Structure

```
Pehance/
├── frontend/          # Next.js application
│   ├── src/
│   │   ├── app/      # App router pages
│   │   ├── components/ # React components
│   │   └── lib/      # Utilities and config
│   └── public/       # Static assets
├── backend/          # FastAPI application
│   ├── main.py       # Main application file
│   └── requirements.txt
└── documentation/    # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- Python 3.9+
- pnpm (recommended) or npm

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Start the development server:
   ```bash
   pnpm dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python main.py
   ```

## 🔧 Development

### Running Tests

```bash
# Frontend tests
cd frontend
pnpm test

# Backend tests (when implemented)
cd backend
python -m pytest
```

### Code Quality

```bash
# Frontend linting
cd frontend
pnpm lint

# Format code
pnpm format
```

## 📝 Documentation

- [Current Status](./documentation/current_status.md)
- [Development Standards](./documentation/development_standards.md)
- [End Goal](./documentation/end_goal.md)
- [Implementation Guide](./documentation/implement.md)
- [Short Term Goals](./documentation/short_term_goal.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern web technologies
- Powered by AI models from Groq and OpenAI
- Inspired by the need for better AI-powered tools 