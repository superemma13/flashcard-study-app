# Configuration Examples

## Backend Configuration

### Development Environment (.env)

```env
# Database
DATABASE_URL=sqlite:///./flashcards.db

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ollama/LLM
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Frontend
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Production Environment (.env.production)

```env
# Database - PostgreSQL recommended
DATABASE_URL=postgresql://user:password@db.example.com:5432/flashcards

# Security
SECRET_KEY=your-long-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Ollama/LLM
OLLAMA_API_URL=https://ollama.example.com
OLLAMA_MODEL=mistral

# Frontend
FRONTEND_URL=https://yourusername.github.io/flashcard-study-app

# Environment
ENVIRONMENT=production
DEBUG=false
```

## Frontend Configuration

### Development Environment (.env.local)

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

### Production Environment (.env.production)

```env
REACT_APP_API_URL=https://your-backend.vercel.app/api
REACT_APP_ENVIRONMENT=production
```

### GitHub Pages Environment (.env.github)

```env
REACT_APP_API_URL=https://your-backend-api.com/api
REACT_APP_ENVIRONMENT=production
```

## GitHub Secrets Configuration

Set these in repository Settings → Secrets and variables → Actions:

```
REACT_APP_API_URL = https://your-api.vercel.app/api
DATABASE_URL = postgresql://...
SECRET_KEY = your-secret-key
OLLAMA_API_URL = https://ollama.example.com
OLLAMA_MODEL = mistral
VERCEL_TOKEN = your-vercel-token
```

## Vercel Environment Variables

Set in Vercel Dashboard → Project Settings → Environment Variables:

```
DATABASE_URL = postgresql://user:password@host/db
SECRET_KEY = your-secure-random-key
OLLAMA_API_URL = https://ollama.example.com
OLLAMA_MODEL = mistral
FRONTEND_URL = https://yourusername.github.io/app
ENVIRONMENT = production
```

## Docker Configuration (Optional)

### Dockerfile (Backend)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: flashcards
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/flashcards
      SECRET_KEY: your-secret-key
      OLLAMA_API_URL: http://ollama:11434
    depends_on:
      - postgres
      - ollama

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000/api

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  ollama_data:
```

Run with:
```bash
docker-compose up
```

## Nginx Configuration (Reverse Proxy)

### nginx.conf

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # API endpoints
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    }

    # Frontend static files
    location / {
        alias /var/www/flashcard-app/;
        try_files $uri $uri/ /index.html;
    }
}
```

## Database Backup Configuration

### PostgreSQL Backup Script

```bash
#!/bin/bash
# backup-db.sh

DB_NAME="flashcards"
DB_USER="user"
BACKUP_DIR="/backups/flashcards"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

pg_dump -U $DB_USER -d $DB_NAME -F c -b -v -f "$BACKUP_DIR/backup_$DATE.dump"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.dump" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/backup_$DATE.dump"
```

Schedule with cron:
```cron
# Run daily at 2 AM
0 2 * * * /path/to/backup-db.sh
```

## Monitoring Configuration

### Sentry Integration (Error Tracking)

Backend (app/main.py):
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

Frontend (src/index.js):
```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: "production",
  tracesSampleRate: 1.0,
});
```

### Application Logging

Backend (app/main.py):
```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'app.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
logger.addHandler(handler)
```

## Performance Tuning

### Database Query Optimization

```python
# Use eager loading
from sqlalchemy.orm import joinedload

cards = db.query(FlashcardDB)\
    .options(joinedload(FlashcardDB.owner))\
    .filter(FlashcardDB.user_id == user_id)\
    .all()

# Add indexes
class FlashcardDB(Base):
    __tablename__ = "flashcards"
    
    # Index frequently searched fields
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    topic = Column(String, index=True)
    difficulty = Column(String, index=True)
    last_reviewed = Column(DateTime, index=True)
```

### Frontend Bundle Optimization

```javascript
// Code splitting with React.lazy
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Study = React.lazy(() => import('./pages/Study'));

// Use Suspense
<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
  </Routes>
</Suspense>
```

### Caching Strategy

```python
# Cache flashcards list
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_topics(user_id: int):
    return db.query(FlashcardDB.topic).filter(
        FlashcardDB.user_id == user_id
    ).distinct().all()
```

## API Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/flashcards/")
@limiter.limit("100/minute")
def get_flashcards(request: Request):
    pass
```

## Security Headers

```python
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

See [DEPLOYMENT.md](./DEPLOYMENT.md) and [DEVELOPMENT.md](./DEVELOPMENT.md) for more information.
