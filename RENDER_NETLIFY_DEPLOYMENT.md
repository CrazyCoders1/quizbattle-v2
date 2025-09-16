# 🚀 QuizBattle Deployment Guide - Render + Netlify

This guide shows how to deploy QuizBattle without Docker to **Render** (backend) and **Netlify** (frontend).

---

## 🎯 Prerequisites

1. **GitHub Repository**: Your code must be pushed to GitHub
2. **Neon PostgreSQL**: Database URL ready (already configured in `.env`)
3. **MongoDB Atlas**: MongoDB connection string ready (already configured in `.env`)
4. **Render Account**: Free account at [render.com](https://render.com)
5. **Netlify Account**: Free account at [netlify.com](https://netlify.com)

---

## 📋 Deployment Steps

### Step 1: Prepare Repository

Your repository is now configured for Render/Netlify deployment:

```
quizbattle/
├── Procfile                    # ✅ For Render
├── netlify.toml               # ✅ For Netlify  
├── render.yaml                # ✅ Render Blueprint
├── backend/
│   ├── requirements.txt       # ✅ Python dependencies
│   ├── run.py                 # ✅ Updated for gunicorn
│   └── .env                   # ✅ Environment variables template
└── frontend/
    ├── package.json           # ✅ Cleaned (no proxy)
    └── .env                   # ✅ API URL configuration
```

### Step 2: Deploy Backend to Render

1. **Connect Repository**:
   - Go to [render.com](https://render.com) → New → Web Service
   - Connect your GitHub repository: `https://github.com/CrazyCoders1/quizbattle-v2`
   - Select **Root Directory**: Leave blank (whole repo)

2. **Configure Build**:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn run:app`

3. **Set Environment Variables** (in Render dashboard):
   ```
   JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
   DATABASE_URL=postgresql://neondb_owner:password@ep-crimson-night-a14reavo-pooler.ap-southeast-1.aws.neon.tech/quizbattle?sslmode=require
   MONGO_URI=mongodb+srv://quizbattle-db:password@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0
   FLASK_ENV=production
   PORT=10000
   ```

4. **Deploy**: 
   - Click "Create Web Service"
   - Wait for deployment (~3-5 minutes)
   - Note your backend URL: `https://your-backend-name.onrender.com`

### Step 3: Deploy Frontend to Netlify

1. **Connect Repository**:
   - Go to [netlify.com](https://netlify.com) → New site from Git
   - Connect your GitHub repository: `https://github.com/CrazyCoders1/quizbattle-v2`

2. **Configure Build** (Netlify reads `netlify.toml`):
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Publish directory**: `frontend/build`

3. **Set Environment Variables** (in Netlify dashboard):
   ```
   REACT_APP_API_URL=https://your-backend-name.onrender.com/api
   ```
   ⚠️ **Important**: Replace `your-backend-name` with your actual Render service name!

4. **Deploy**:
   - Click "Deploy site"
   - Wait for build (~2-3 minutes)
   - Note your frontend URL: `https://your-site-name.netlify.app`

---

## 🧪 Testing Deployment

### 1. Test Backend
```bash
# Health check
curl https://your-backend-name.onrender.com/health
# Should return: {"status": "healthy", "timestamp": "...", "version": "1.0.0"}

# Test API endpoints
curl https://your-backend-name.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

### 2. Test Frontend
- Open `https://your-site-name.netlify.app`
- Try registering a new user
- Check browser console for any API connection errors

### 3. Test Full Integration
- Register a new user via frontend
- Login and create a challenge
- Join the challenge from another browser/incognito
- Verify everything works end-to-end

---

## 🔧 Local Development (No Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt
flask run
# Runs on http://localhost:5000
```

### Frontend  
```bash
cd frontend
npm install
npm start  
# Runs on http://localhost:3000
```

---

## 🌍 Environment Variables Summary

### Backend (Render Dashboard)
```
JWT_SECRET=your-secret-key-here
DATABASE_URL=your-neon-postgres-url-here
MONGO_URI=your-mongodb-atlas-url-here
FLASK_ENV=production
PORT=10000
```

### Frontend (Netlify Dashboard)
```
REACT_APP_API_URL=https://your-backend-name.onrender.com/api
```

---

## 🚨 Important Notes

### CORS Configuration
- Backend allows all origins (`*`) for now
- In production, update `CORS(app, origins=["https://your-netlify-domain.netlify.app"])`

### Database Migrations
- Render automatically runs migrations on deploy
- For manual migrations: Use Render shell or run locally

### Monitoring
- **Backend logs**: Render dashboard → Logs tab
- **Frontend logs**: Netlify dashboard → Functions tab
- **Health check**: `https://your-backend-name.onrender.com/health`

### SSL/HTTPS
- ✅ **Render**: Automatic HTTPS for all services
- ✅ **Netlify**: Automatic HTTPS for all sites

---

## 🎉 Success!

Your QuizBattle application should now be live:

- **Backend**: `https://your-backend-name.onrender.com`
- **Frontend**: `https://your-site-name.netlify.app`
- **Status**: Production ready, no Docker required! 

### Next Steps
1. Update CORS origins with your actual Netlify domain
2. Set up custom domain names (optional)
3. Configure monitoring and alerts
4. Set up CI/CD for automatic deployments

---

## 🆘 Troubleshooting

### Backend Issues
- **Build failing**: Check `requirements.txt` has all dependencies
- **App not starting**: Ensure `Procfile` points to `run:app`
- **Database errors**: Verify `DATABASE_URL` and run migrations

### Frontend Issues  
- **Build failing**: Check `package.json` and remove `proxy` field
- **API not connecting**: Verify `REACT_APP_API_URL` environment variable
- **Routes not working**: Ensure `netlify.toml` redirects are configured

### CORS Issues
```
Access to XMLHttpRequest at 'backend-url' from origin 'frontend-url' has been blocked by CORS policy
```
**Solution**: Update backend CORS configuration with your Netlify domain.

---

*Deployment guide for QuizBattle v1.0 - Docker-free hosting* 🎯