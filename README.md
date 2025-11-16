# AI-Powered Flashcard Study App

A full-stack AI-powered flashcard and study application with spaced repetition, adaptive difficulty, and ML integration.

## Features

✨ **Core Features**
- 📝 **Auto-generate Flashcards**: Convert text into flashcards using Ollama LLM
- 🔄 **Spaced Repetition**: SM-2 algorithm for optimal review scheduling
- 🎯 **Adaptive Quiz Mode**: Difficulty adjusts based on your performance
- 👤 **User Accounts**: Register, login, and track your progress
- 📊 **Analytics Dashboard**: View study statistics, streaks, and accuracy

✅ **Technical Features**
- Vector embeddings for semantic search
- Machine learning-based difficulty scoring
- Study session tracking and analytics
- Responsive web interface
- Easy deployment to GitHub Pages or Vercel

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy + SQLite (upgradeable to PostgreSQL)
- **LLM**: Ollama (local LLM API)
- **ML**: scikit-learn for embeddings and similarity

### Frontend
- **Framework**: React 18
- **State Management**: Zustand
- **Styling**: CSS3 with modern features
- **Routing**: React Router v6

## Project Structure

```
flashcard-study-app/
├── backend/
│   ├── app/
│   │   ├── models/           # Pydantic models (schemas)
│   │   ├── routes/           # API endpoints
│   │   ├── services/         # Business logic (LLM, spaced repetition)
│   │   ├── db/              # Database models and auth
│   │   ├── main.py          # FastAPI app
│   │   └── config.py        # Configuration
│   ├── api.py               # Vercel serverless wrapper
│   ├── vercel.json          # Vercel deployment config
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── public/              # Static files
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── styles/          # CSS styles
│   │   ├── api.js           # API client
│   │   ├── store.js         # Zustand store
│   │   ├── App.js           # Main app component
│   │   └── index.js         # Entry point
│   ├── package.json         # Node dependencies
│   └── .env.example         # Example environment variables
├── .github/workflows/       # CI/CD workflows
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Ollama (for LLM flashcard generation)

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd flashcard-study-app
```

#### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env

# Start the backend server
python -m uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

#### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

#### 4. Setup Ollama (for LLM features)

```bash
# Download and install Ollama from https://ollama.ai

# Pull a model (Mistral is recommended for speed)
ollama pull mistral

# Start Ollama service
ollama serve
```

Ollama will be available at `http://localhost:11434`

### Running the Application

1. **Start Ollama** (in a terminal):
   ```bash
   ollama serve
   ```

2. **Start Backend** (in another terminal):
   ```bash
   cd backend
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   python -m uvicorn app.main:app --reload
   ```

3. **Start Frontend** (in another terminal):
   ```bash
   cd frontend
   npm start
   ```

4. **Access the App**: Open `http://localhost:3000` in your browser

## Usage

### Creating Flashcards

1. **Manual Creation**: Go to "Manage Flashcards" and create cards one by one
2. **AI Generation**: Use "Generate from Text" to automatically create flashcards from any text using Ollama

### Study Session

1. Click "Start Studying" on the dashboard
2. Select a topic (optional)
3. Study cards with spaced repetition algorithm
4. Mark answers as correct or incorrect
5. Difficulty adjusts automatically based on performance

### Analytics

View your study progress:
- Total cards studied
- Study sessions completed
- Average accuracy
- Current study streak
- Cards due for review
- Accuracy by topic

## Spaced Repetition Algorithm

The app implements a modified SM-2 algorithm:

1. **Initial intervals**: 1 day for first review, 3 days for second
2. **Easiness factor**: Adjusts between 1.3 and 2.5 based on performance
3. **Difficulty scoring**: Updated with each review based on correctness and response time
4. **Adaptive selection**: Prioritizes cards due for review and matches user's difficulty preference

## Adaptive Difficulty

Quiz difficulty automatically adjusts:
- **>80% accuracy**: Increase difficulty
- **60-80% accuracy**: Maintain medium difficulty
- **<60% accuracy**: Decrease difficulty

## Deployment

### Deploy Frontend to GitHub Pages

1. Update `homepage` in `frontend/package.json`:
   ```json
   "homepage": "https://yourusername.github.io/flashcard-study-app"
   ```

2. Set up GitHub Actions secrets:
   - `REACT_APP_API_URL`: Your backend URL

3. Push to main branch - GitHub Actions will automatically build and deploy

### Deploy Backend to Vercel

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   cd backend
   vercel
   ```

3. Set environment variables in Vercel dashboard:
   - `DATABASE_URL`: PostgreSQL connection string (recommended for Vercel)
   - `SECRET_KEY`: Random secret key
   - `OLLAMA_API_URL`: Your Ollama server URL
   - `FRONTEND_URL`: Your frontend URL

4. Update `REACT_APP_API_URL` in frontend `.env.local`

### Environment Variables

**Backend (.env)**:
```
DATABASE_URL=sqlite:///./flashcards.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

**Frontend (.env.local)**:
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Flashcards
- `GET /api/flashcards/` - Get all flashcards
- `POST /api/flashcards/` - Create flashcard
- `PUT /api/flashcards/{id}` - Update flashcard
- `DELETE /api/flashcards/{id}` - Delete flashcard
- `POST /api/flashcards/generate-from-text` - Generate from text using LLM

### Study Sessions
- `POST /api/study/session/start` - Start study session
- `GET /api/study/cards-for-session/{id}` - Get cards for session
- `POST /api/study/quiz/answer` - Submit quiz answer
- `GET /api/study/adaptive-difficulty/{id}` - Get recommended difficulty

### Analytics
- `GET /api/analytics/dashboard` - Get user analytics
- `GET /api/analytics/cards-by-difficulty` - Get cards grouped by difficulty

## Features Breakdown

### 1. Auto-generate Flashcards ✅
- Upload text via web interface
- Ollama LLM generates Q&A pairs
- Specify difficulty level
- Automatically saves to database

### 2. Spaced Repetition ✅
- SM-2 algorithm implementation
- Next review date calculation
- Easiness factor tracking
- Randomized intervals to prevent clustering

### 3. User Accounts ✅
- JWT-based authentication
- Secure password hashing (bcrypt)
- User-specific flashcard collections
- Session tracking

### 4. Quiz Mode with Adaptive Difficulty ✅
- Real-time difficulty adjustment
- Accuracy-based recommendations
- Response time tracking
- Question selection using spaced repetition

### 5. Analytics ✅
- Study session statistics
- Daily study minutes
- Accuracy by topic
- Study streak tracking
- Cards due for review

## Development

### Adding New Features

1. **Backend**:
   - Add models in `backend/app/models/`
   - Add routes in `backend/app/routes/`
   - Update database in `backend/app/db/__init__.py`

2. **Frontend**:
   - Add pages in `frontend/src/pages/`
   - Add styles in `frontend/src/styles/`
   - Update routes in `frontend/src/App.js`

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Building for Production

**Frontend**:
```bash
cd frontend
npm run build
```

**Backend**:
- The Vercel configuration handles building automatically
- Or use Docker for containerization

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_API_URL` in backend `.env`
- Test connection: `curl http://localhost:11434/api/tags`

### CORS Errors
- Update `ALLOWED_ORIGINS` in backend `config.py`
- Ensure frontend URL is in the list

### Database Errors
- Delete `flashcards.db` to reset database
- Ensure SQLite is writable

### Frontend Build Issues
- Clear node_modules: `rm -rf node_modules` and `npm install`
- Clear cache: `npm cache clean --force`

## Future Enhancements

- 📱 Mobile app (React Native)
- 🗣️ Pronunciation audio for language learning
- 🎨 Custom themes and UI customization
- 🔍 Full-text search across flashcards
- 🏆 Leaderboards and social features
- 📤 Import/export flashcards (CSV, JSON)
- 🎓 Class/group management for teachers
- 🤖 More advanced ML for better difficulty prediction

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an GitHub issue
- Check existing documentation
- Review troubleshooting section

## Acknowledgments

- FastAPI - Modern web framework
- React - UI library
- Ollama - Local LLM support
- SM-2 algorithm - Spaced repetition foundation

---

Built with ❤️ for learners everywhere
