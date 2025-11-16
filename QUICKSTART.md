# Quick Start Guide

Get the Flashcard Study App running in 5 minutes!

## System Requirements

- ✅ Python 3.9 or higher
- ✅ Node.js 16 or higher  
- ✅ Git
- ✅ Ollama (for LLM flashcard generation)

## Option 1: Quick Local Setup (Linux/macOS)

### 1. Clone & Navigate

```bash
git clone <repository-url>
cd flashcard-study-app
```

### 2. Setup Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Setup Frontend

```bash
cd ../frontend
npm install
cp .env.example .env.local
```

### 4. Run Everything

**Terminal 1 - Ollama**:
```bash
ollama serve
```

**Terminal 2 - Backend**:
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

**Terminal 3 - Frontend**:
```bash
cd frontend
npm start
```

### 5. Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Option 2: Quick Local Setup (Windows)

### 1. Clone & Navigate

```powershell
git clone <repository-url>
cd flashcard-study-app
```

### 2. Setup Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 3. Setup Frontend

```powershell
cd ..\frontend
npm install
copy .env.example .env.local
```

### 4. Run Everything

**Terminal 1 - Ollama**:
```powershell
ollama serve
```

**Terminal 2 - Backend**:
```powershell
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

**Terminal 3 - Frontend**:
```powershell
cd frontend
npm start
```

### 5. Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## First Steps

### 1. Register an Account

1. Go to http://localhost:3000
2. Click "Register here"
3. Fill in email, username, password
4. Click "Register"

### 2. Create Flashcards

**Method A: Manual**
1. Click "Manage Flashcards"
2. Add cards one by one
3. Set topic and difficulty

**Method B: AI Generation** ⚡
1. Click "Generate from Text"
2. Paste or type content
3. Set topic and number of cards
4. Click "Generate Flashcards"
5. Ollama will create cards from your text!

### 3. Study

1. Go to Dashboard
2. Click "Start Studying"
3. Select a topic (or all)
4. Study flashcards with spaced repetition
5. Mark answers as correct/incorrect
6. Watch difficulty adapt to your performance

### 4. Check Progress

Click "View Analytics" to see:
- Total cards studied
- Study sessions completed
- Your accuracy percentage
- Study streak
- Cards due for review
- Accuracy by topic

---

## Troubleshooting

### "Cannot connect to Ollama"

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Verify connection:
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. Check `.env` file has correct `OLLAMA_API_URL`

### "Module not found" (Backend)

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### "npm ERR!" (Frontend)

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### "Port already in use"

Change ports in commands:
```bash
# Backend on different port
python -m uvicorn app.main:app --reload --port 8001

# Frontend on different port
PORT=3001 npm start
```

---

## Deployment Quick Links

- **Frontend to GitHub Pages**: See [DEPLOYMENT.md](./DEPLOYMENT.md#github-pages-deployment-frontend)
- **Backend to Vercel**: See [DEPLOYMENT.md](./DEPLOYMENT.md#vercel-deployment-backend)

---

## Project Structure at a Glance

```
flashcard-study-app/
├── backend/           ← FastAPI server (Python)
│   ├── app/
│   │   ├── models/    ← Data schemas
│   │   ├── routes/    ← API endpoints
│   │   ├── services/  ← Business logic
│   │   └── db/        ← Database models
│   └── requirements.txt
├── frontend/          ← React app (JavaScript)
│   ├── src/
│   │   ├── pages/     ← React components
│   │   ├── styles/    ← CSS files
│   │   ├── api.js     ← API client
│   │   └── store.js   ← State management
│   └── package.json
├── README.md          ← Full documentation
├── DEPLOYMENT.md      ← Deployment guide
└── DEVELOPMENT.md     ← Developer guide
```

---

## Key Features

✨ **What You Get**

- 🤖 AI-powered flashcard generation from any text
- 📚 Spaced repetition algorithm for optimal learning
- 🎯 Adaptive quiz difficulty based on your performance
- 👤 User accounts with secure authentication
- 📊 Analytics dashboard with study statistics
- 🚀 Deployment ready for GitHub Pages + Vercel
- 🔒 Secure, modern tech stack
- 📱 Responsive design works on desktop & tablet

---

## Next Steps

1. **Read the docs**: Check [README.md](./README.md) for complete documentation
2. **Deploy**: Follow [DEPLOYMENT.md](./DEPLOYMENT.md) to go live
3. **Customize**: See [DEVELOPMENT.md](./DEVELOPMENT.md) to add features
4. **Contribute**: Submit PRs for improvements!

---

## Need Help?

- 📖 Check [README.md](./README.md) for comprehensive docs
- 🚀 See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment help
- 👨‍💻 See [DEVELOPMENT.md](./DEVELOPMENT.md) for development questions
- 🐛 Open a GitHub issue for bugs

---

**Happy studying! 🎓**

Built with FastAPI + React + Ollama 💚
