# Development Guide

This guide covers setting up the development environment and extending the application.

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- Git
- VS Code or favorite editor

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd flashcard-study-app

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env

# Setup frontend
cd ../frontend
npm install
cp .env.example .env.local

# Start Ollama (separate terminal)
ollama serve

# Start backend (from backend directory)
python -m uvicorn app.main:app --reload

# Start frontend (from frontend directory)
npm start
```

## Project Architecture

### Backend Architecture

```
app/
├── main.py          # FastAPI app initialization
├── config.py        # Settings and configuration
├── models/          # Pydantic schemas
│   ├── user.py
│   ├── flashcard.py
│   ├── study_session.py
│   ├── quiz_attempt.py
│   └── analytics.py
├── routes/          # API endpoints
│   ├── auth.py
│   ├── flashcards.py
│   ├── study.py
│   └── analytics.py
├── services/        # Business logic
│   ├── spaced_repetition.py
│   ├── llm_service.py
│   └── __init__.py
└── db/             # Database
    ├── __init__.py  # SQLAlchemy models
    └── auth.py     # Authentication utilities
```

### Frontend Architecture

```
src/
├── pages/           # React components (pages)
│   ├── Login.js
│   ├── Register.js
│   ├── Dashboard.js
│   ├── Study.js
│   └── GenerateFlashcards.js
├── styles/          # CSS styles
│   ├── Auth.css
│   ├── Dashboard.css
│   ├── Study.css
│   └── GenerateFlashcards.css
├── api.js           # API client
├── store.js         # Zustand state management
├── App.js           # Main app component
└── index.js         # React entry point
```

## Adding Features

### Adding a New Backend Endpoint

1. **Create the model** in `app/models/`:

```python
# app/models/example.py
from pydantic import BaseModel

class ExampleCreate(BaseModel):
    name: str
    description: str

class ExampleResponse(BaseModel):
    id: int
    name: str
    description: str
    
    class Config:
        from_attributes = True
```

2. **Update database models** in `app/db/__init__.py`:

```python
class ExampleDB(Base):
    __tablename__ = "examples"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
```

3. **Create routes** in `app/routes/example.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db, ExampleDB
from app.models import ExampleCreate, ExampleResponse

router = APIRouter(prefix="/api/examples", tags=["examples"])

@router.get("/", response_model=list[ExampleResponse])
def get_examples(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    examples = db.query(ExampleDB).filter(ExampleDB.user_id == user.id).all()
    return [ExampleResponse.from_orm(e) for e in examples]

@router.post("/", response_model=ExampleResponse)
def create_example(data: ExampleCreate, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    example = ExampleDB(user_id=user.id, name=data.name, description=data.description)
    db.add(example)
    db.commit()
    db.refresh(example)
    return ExampleResponse.from_orm(example)
```

4. **Include router** in `app/main.py`:

```python
from app.routes import example
app.include_router(example.router)
```

### Adding a New Frontend Page

1. **Create page component** in `src/pages/ExamplePage.js`:

```javascript
import React, { useState, useEffect } from 'react';
import api from '../api';
import '../styles/ExamplePage.css';

function ExamplePage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      const data = await api.getExamples();
      setItems(data);
    } catch (error) {
      console.error('Failed to load items:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="example-page">
      {/* Page content */}
    </div>
  );
}

export default ExamplePage;
```

2. **Add API methods** in `src/api.js`:

```javascript
async getExamples() {
  return this.request('GET', `/examples?token=${this.token}`);
}

async createExample(name, description) {
  return this.request('POST', '/examples?token=' + this.token, {
    name,
    description
  });
}
```

3. **Add route** in `src/App.js`:

```javascript
import ExamplePage from './pages/ExamplePage';

// In Routes:
<Route path="/examples" element={<ExamplePage />} />
```

4. **Add styles** in `src/styles/ExamplePage.css`

## Testing

### Backend Testing

```bash
cd backend

# Install pytest
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

Example test:

```python
# tests/test_auth.py
import pytest
from app.db.auth import hash_password, verify_password

def test_password_hashing():
    password = "test_password_123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
```

### Frontend Testing

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## Database Migrations

Using Alembic for database schema changes:

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Variables

### Development

**Backend (.env)**:
```
DATABASE_URL=sqlite:///./flashcards.db
SECRET_KEY=dev-secret-key-only-for-development
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
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

## Code Style

### Python (Backend)

```bash
# Format with Black
pip install black
black app/

# Lint with Flake8
pip install flake8
flake8 app/

# Type checking with mypy
pip install mypy
mypy app/
```

### JavaScript (Frontend)

```bash
# Format with Prettier
npm install --save-dev prettier
npx prettier --write src/

# Lint with ESLint
npm run lint

# Fix linting issues
npm run lint -- --fix
```

## Debugging

### Backend Debugging

```python
# Use Python debugger
import pdb; pdb.set_trace()

# Or use FastAPI's built-in debugging
# Set DEBUG=True in config.py for development
```

### Frontend Debugging

```javascript
// Use console.log
console.log('Debug info:', data);

// Use browser DevTools
debugger;  // Will pause execution

// Use React DevTools extension
```

## Performance Optimization

### Backend

1. **Database Query Optimization**:
   - Use eager loading for relationships
   - Add database indexes
   - Cache frequently accessed data

2. **Response Compression**:
   - Enable gzip compression
   - Use response pagination

3. **Async Operations**:
   - Use async/await for I/O operations
   - Implement background tasks

### Frontend

1. **Bundle Size**:
   - Code splitting with React.lazy
   - Remove unused dependencies
   - Minify and compress assets

2. **Rendering Performance**:
   - Memoize expensive components
   - Use virtualization for large lists
   - Optimize re-renders

## Useful Commands

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000
python -m pytest
python -m black app/
python -m flake8 app/

# Frontend
cd frontend
npm start           # Development server
npm run build       # Production build
npm test            # Run tests
npm run eject       # Eject from Create React App

# Git
git status
git add .
git commit -m "message"
git push origin main
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add my feature"

# Push to remote
git push origin feature/my-feature

# Create pull request on GitHub
# After review and merge, delete branch
git branch -d feature/my-feature
```

## Documentation

Keep documentation updated:
- Update README.md for user-facing changes
- Update DEPLOYMENT.md for deployment changes
- Add inline code comments for complex logic
- Keep API docs in sync with code

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Python Best Practices](https://pep8.org/)
- [JavaScript Best Practices](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)

## Getting Help

1. Check existing documentation
2. Search GitHub issues
3. Check Stack Overflow
4. Open a GitHub issue with details
5. Contact maintainers

