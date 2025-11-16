# Deployment Guide

This guide covers deploying the Flashcard Study App to GitHub Pages (frontend) and Vercel (backend).

## GitHub Pages Deployment (Frontend)

### Step 1: Prepare Your Repository

1. Create a GitHub repository named `flashcard-study-app`
2. Push your code to the `main` branch

### Step 2: Configure Frontend

Update `frontend/package.json`:

```json
{
  "homepage": "https://yourusername.github.io/flashcard-study-app",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}
```

### Step 3: Setup GitHub Actions

The workflow file is already created at `.github/workflows/deploy-frontend.yml`.

Add these GitHub Secrets:
1. Go to Settings → Secrets and variables → Actions
2. Add `REACT_APP_API_URL`: Your backend API URL

### Step 4: Deploy

Push to main branch - GitHub Actions will automatically:
1. Build the React app
2. Deploy to GitHub Pages

Your app will be available at: `https://yourusername.github.io/flashcard-study-app`

## Vercel Deployment (Backend)

### Step 1: Create Vercel Account

1. Sign up at https://vercel.com
2. Connect your GitHub account

### Step 2: Create PostgreSQL Database

For production, use PostgreSQL instead of SQLite:

1. Use Vercel's PostgreSQL integration or external provider
2. Get your connection string: `postgresql://user:password@host:port/db`

### Step 3: Deploy Backend

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd backend
vercel
```

### Step 4: Set Environment Variables

In Vercel dashboard:

1. Go to your project settings
2. Add environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: Generate a random secret (32+ characters)
   - `OLLAMA_API_URL`: Your Ollama server URL (or ngrok tunnel)
   - `FRONTEND_URL`: Your GitHub Pages URL
   - `ENVIRONMENT`: `production`

### Step 5: Update Frontend

Update `frontend/.env.local`:

```
REACT_APP_API_URL=https://your-vercel-app.vercel.app/api
```

## Running Ollama on a Server

For remote Ollama access, use ngrok:

```bash
# Install ngrok: https://ngrok.com

# In terminal with Ollama running
ollama serve

# In another terminal
ngrok http 11434

# Use the ngrok URL as OLLAMA_API_URL
# Example: https://abc123.ngrok.io
```

## Database Migration

### From SQLite to PostgreSQL

1. Export data from SQLite
2. Create PostgreSQL database
3. Update `DATABASE_URL` to PostgreSQL connection string
4. FastAPI/SQLAlchemy will handle schema creation

## Monitoring

### GitHub Actions

Check deployment status:
1. Go to your GitHub repository
2. Click "Actions" tab
3. View workflow runs

### Vercel

Monitor your backend:
1. Log into Vercel dashboard
2. View function logs and analytics
3. Check performance metrics

## Troubleshooting

### Frontend Deploy Issues

**Problem**: Build fails
- Solution: Check `npm run build` locally first
- Solution: Ensure all dependencies are in `package.json`

**Problem**: Blank page after deploy
- Solution: Check browser console for API errors
- Solution: Verify `REACT_APP_API_URL` is set correctly

### Backend Deploy Issues

**Problem**: 502 Bad Gateway
- Solution: Check Vercel logs for errors
- Solution: Ensure all environment variables are set
- Solution: Check database connectivity

**Problem**: LLM generation fails
- Solution: Ensure Ollama is accessible
- Solution: Check `OLLAMA_API_URL` is correct
- Solution: Verify Ollama model is available

### CORS Issues

If you see CORS errors:

1. Update backend `ALLOWED_ORIGINS` in `config.py`
2. Add your frontend URL to the list
3. Redeploy backend

Example:
```python
ALLOWED_ORIGINS = [
    "https://yourusername.github.io",
    "https://your-vercel-app.vercel.app"
]
```

## Scaling

### Add More Computational Resources

1. Vercel: Upgrade to Vercel Pro for more resources
2. Database: Consider managed PostgreSQL services
3. Ollama: Run on dedicated GPU server

### Caching

Implement response caching:

```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

# Configure caching in production
```

## Backup & Monitoring

### Database Backups

1. Set up automated PostgreSQL backups
2. Export/import data regularly
3. Test restore procedures

### Monitoring

Use monitoring services:
- Sentry for error tracking
- DataDog or New Relic for performance
- GitHub Actions logs for deployment tracking

## Custom Domain

### GitHub Pages

1. Add CNAME file to `frontend/public/CNAME`:
   ```
   yourapp.com
   ```

2. Update DNS records to point to GitHub Pages

### Vercel

1. Go to project settings
2. Add custom domain
3. Update DNS records with provided values

## SSL/HTTPS

Both GitHub Pages and Vercel automatically provide SSL certificates.

## Performance Optimization

### Frontend

```bash
cd frontend
npm run build -- --analyze  # Analyze bundle size
```

### Backend

- Use connection pooling for database
- Implement caching for frequently accessed data
- Optimize LLM queries with rate limiting

## Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://react.dev/learn/start-a-new-react-project)
