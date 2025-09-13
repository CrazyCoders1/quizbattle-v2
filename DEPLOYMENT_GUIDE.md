# QuizBattle Production Deployment Guide

This guide will help you deploy QuizBattle to a production environment using Docker and Docker Compose.

## 🚀 Quick Start

1. **Clone and Navigate**
   ```bash
   git clone <your-repo>
   cd quizbattle
   ```

2. **Configure Environment**
   ```bash
   cp backend/.env.production.example backend/.env.production
   cp frontend/.env.production.example frontend/.env.production
   # Edit these files with your production values
   ```

3. **Deploy**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- OpenSSL (for SSL certificates)
- 4GB+ RAM
- 20GB+ disk space

## ⚙️ Configuration

### Backend Environment (.env.production)

```bash
# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-production-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DEFAULT_ADMIN_PASSWORD=secure-admin-password

# Database
POSTGRES_PASSWORD=secure-postgres-password
MONGO_PASSWORD=secure-mongo-password

# OpenRouter AI (Required for PDF extraction)
OPENROUTER_API_KEY=your-openrouter-api-key

# Domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Frontend Environment (.env.production)

```bash
REACT_APP_API_URL=https://api.yourdomain.com/api
REACT_APP_BASE_URL=https://yourdomain.com
PUBLIC_URL=https://yourdomain.com
```

## 🏗️ Architecture

```
Internet → Nginx (SSL/TLS) → Frontend (React) / Backend (Flask)
                          ↓
                     PostgreSQL + MongoDB + Redis
```

## 📦 Services

| Service | Port | Purpose |
|---------|------|---------|
| Nginx | 80/443 | Reverse proxy, SSL termination |
| Frontend | 3000 | React application |
| Backend | 5000 | Flask API server |
| PostgreSQL | 5432 | Main database |
| MongoDB | 27017 | Logging and analytics |
| Redis | 6379 | Caching and rate limiting |

## 🔐 Security Features

- **SSL/TLS** encryption (HTTPS only)
- **Rate limiting** on API endpoints
- **CORS** protection
- **Security headers** (HSTS, XSS protection, etc.)
- **JWT** authentication with secure tokens
- **Input validation** and sanitization
- **SQL injection** protection

## 📊 Monitoring

### Health Checks
- Frontend: `https://yourdomain.com/health`
- Backend: `https://yourdomain.com/api/health`

### Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Service Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

## 🗄️ Database Management

### Backup PostgreSQL
```bash
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U quizbattle_user quizbattle_prod > backup.sql
```

### Restore PostgreSQL
```bash
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U quizbattle_user quizbattle_prod < backup.sql
```

### Database Migrations
```bash
docker-compose -f docker-compose.prod.yml exec backend flask db upgrade
```

## 🚀 Deployment Commands

### Initial Deployment
```bash
./deploy.sh
```

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up --build -d

# Run any new migrations
docker-compose -f docker-compose.prod.yml exec backend flask db upgrade
```

### Scale Services
```bash
# Scale backend to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Complete Reset (⚠️ DATA LOSS)
```bash
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a
```

## 📈 Performance Tuning

### Backend (Flask + Gunicorn)
- **Workers**: Set based on CPU cores (2 × cores + 1)
- **Timeout**: 120s for PDF processing
- **Memory**: 512MB per worker

### Frontend (React + Nginx)
- **Gzip compression** enabled
- **Static asset caching** (1 year)
- **CDN integration** recommended

### Database (PostgreSQL)
- **Connection pooling** via SQLAlchemy
- **Query optimization** with indexes
- **Regular VACUUM** operations

## 🔧 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs SERVICE_NAME

# Check container status
docker ps -a

# Restart specific service
docker-compose -f docker-compose.prod.yml restart SERVICE_NAME
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U quizbattle_user -d quizbattle_prod -c "SELECT version();"

# Test MongoDB connection
docker-compose -f docker-compose.prod.yml exec mongodb mongo --eval "db.runCommand({connectionStatus: 1})"
```

### PDF Upload Issues
```bash
# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend | grep -i pdf

# Verify OpenRouter API key
docker-compose -f docker-compose.prod.yml exec backend python -c "import os; print(os.environ.get('OPENROUTER_API_KEY', 'NOT SET'))"
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check Nginx error logs
docker-compose -f docker-compose.prod.yml logs nginx | grep error
```

## 🛡️ Security Checklist

- [ ] Changed all default passwords
- [ ] Using strong SSL certificates (not self-signed)
- [ ] Environment variables secured
- [ ] Database access restricted
- [ ] Regular security updates
- [ ] Backup strategy implemented
- [ ] Log monitoring configured
- [ ] Rate limiting configured
- [ ] HTTPS redirects working

## 📱 Admin Access

After deployment:
1. Visit `https://yourdomain.com/admin`
2. Login with admin credentials from `.env.production`
3. Upload JEE PDF papers via "Upload PDF" tab
4. Create challenges and manage questions

## 🆘 Support

### Common Issues

**Q: PDF extraction not working**
A: Check OpenRouter API key and ensure AI models are accessible

**Q: Frontend shows API errors**
A: Verify `REACT_APP_API_URL` matches your backend URL

**Q: Database errors on startup**
A: Ensure PostgreSQL container is fully ready before backend starts

**Q: SSL certificate errors**
A: Replace self-signed certificates with real ones from Let's Encrypt

### Getting Help
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify configuration files
3. Test individual services
4. Check firewall and network settings

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [React Deployment](https://create-react-app.dev/docs/deployment/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)

---

🎉 **QuizBattle is now ready for production!**

Visit your domain to start creating JEE quizzes and challenges.