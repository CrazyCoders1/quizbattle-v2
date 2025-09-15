# QuizBattle Render Deployment Guide

## Overview
This guide covers the updated configuration for deploying QuizBattle to Render using Python 3.12, psycopg3, and managed PostgreSQL/Redis services.

## Key Changes Made

### 1. Updated Requirements (`requirements.txt`)
- **Python 3.12+ compatible** dependencies
- **Replaced psycopg2 with psycopg3**: `psycopg[binary,pool]>=3.2`
- Updated Flask and SQLAlchemy to latest stable versions
- Added proper connection pooling and security packages

### 2. Updated Render Configuration (`render.yaml`)
- **Python 3.12 runtime** specified
- **Managed PostgreSQL service** (free tier compatible)
- **Redis service** for caching and logging (MongoDB alternative for free tier)
- **Automatic database migrations** during build: `flask db upgrade`
- **Production-ready start command**: `gunicorn -w 4 -b 0.0.0.0:10000 app:app`

### 3. Backend Configuration Updates
- **psycopg3 compatibility**: Handles `postgres://` to `postgresql://` URL conversion
- **Connection pooling**: Added `pool_pre_ping` and `pool_recycle` for reliability
- **SSL support**: Automatic SSL configuration for production databases
- **Redis fallback**: Uses Redis instead of MongoDB for logging on free tier
- **Graceful degradation**: Handles connection failures without crashing

### 4. Clean Deployment Structure
- **No Docker dependencies**: Pure Render deployment
- **Automated migrations**: Database setup handled during build
- **Environment variables**: All secrets managed via Render dashboard
- **Production logging**: Structured logging with fallback options

## Deployment Steps

### 1. Connect Repository to Render
1. Fork/clone this repository to your GitHub account
2. Connect your Render account to GitHub
3. Create new service from `render.yaml`

### 2. Environment Variables
The following will be automatically set by `render.yaml`:
- `PYTHON_VERSION=3.12`
- `FLASK_ENV=production`
- `PORT=10000`
- `DATABASE_URL` (from PostgreSQL service)
- `REDIS_URL` (from Redis service)
- `JWT_SECRET` (auto-generated)

### 3. Services Created
1. **quizbattle-postgres** - PostgreSQL database (free tier)
2. **quizbattle-redis** - Redis cache/logging (free tier) 
3. **quizbattle-backend** - Flask web service (free tier)

### 4. Build Process
The build automatically:
1. Installs Python 3.12 dependencies
2. Runs `flask db upgrade` for database migrations
3. Sets up connection pooling and SSL
4. Configures logging and error handling

### 5. Production Features
- **4 Gunicorn workers** for better performance
- **Connection pooling** with auto-retry
- **SSL/TLS encryption** for database connections
- **Rate limiting** and CORS protection
- **Health check endpoints** (`/health`)
- **Structured logging** with Redis fallback

## Local Development

To run locally with the new configuration:

```bash
cd backend
pip install -r ../requirements.txt
export FLASK_APP=app.py
export FLASK_ENV=development
export DATABASE_URL="postgresql://user:pass@localhost:5432/quizbattle"
flask db upgrade
python run.py
```

## Troubleshooting

### Common Issues
1. **Migration errors**: Ensure all models are imported in `run.py`
2. **Connection issues**: Check DATABASE_URL format (should start with `postgresql://`)
3. **Build failures**: Verify Python 3.12 compatibility of all dependencies
4. **SSL errors**: Production databases require SSL; local dev doesn't

### Logs
- Build logs: Available in Render dashboard during deployment
- Runtime logs: Check Render service logs for application errors
- Database logs: PostgreSQL service logs in Render dashboard

## Cost Optimization
- **Free tier**: All services configured for Render free tier
- **Connection pooling**: Reduces database connection overhead
- **Redis caching**: Improves performance and reduces database load
- **Health checks**: Prevents unnecessary restarts

## Security Features
- **Auto-generated JWT secrets**
- **SSL/TLS for all database connections**
- **CORS protection** with configurable origins
- **Rate limiting** on API endpoints
- **Environment-based configuration**

The deployment is now ready for production use with minimal configuration required!