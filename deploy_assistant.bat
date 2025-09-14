@echo off
echo 🚀 QuizBattle Deployment Assistant
echo ==================================

echo.
echo ✅ Repository Status: Code pushed to GitHub
echo 📂 Repository URL: https://github.com/CrazyCoders1/quizbattle
echo.

echo 🔧 STEP 1: Deploy Backend to Render
echo ------------------------------------
echo 1. Open: https://render.com
echo 2. Sign up and connect your GitHub account
echo 3. Create new Web Service
echo 4. Connect repository: CrazyCoders1/quizbattle
echo 5. Configure:
echo    - Name: quizbattle-backend
echo    - Runtime: Python 3
echo    - Build Command: pip install -r backend/requirements.txt
echo    - Start Command: cd backend && gunicorn run:app
echo.

echo 🌍 Environment Variables for Render:
echo JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
echo DATABASE_URL=postgresql://neondb_owner:password@ep-crimson-night-a14reavo-pooler.ap-southeast-1.aws.neon.tech/quizbattle?sslmode=require
echo MONGO_URI=mongodb+srv://quizbattle-db:password@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0
echo FLASK_ENV=production
echo PORT=10000
echo.

echo 📱 STEP 2: Deploy Frontend to Netlify
echo --------------------------------------
echo 1. Open: https://netlify.com
echo 2. Sign up and connect your GitHub account
echo 3. New site from Git
echo 4. Select repository: CrazyCoders1/quizbattle
echo 5. Netlify will auto-detect netlify.toml settings
echo.

echo 🌍 Environment Variable for Netlify:
echo REACT_APP_API_URL=https://YOUR-BACKEND-URL.onrender.com/api
echo.
echo ⚠️ IMPORTANT: Replace YOUR-BACKEND-URL with actual Render URL!
echo.

echo 🧪 STEP 3: Test Deployment
echo --------------------------
echo After both deployments complete:
echo 1. Test backend health: https://your-backend-url.onrender.com/health
echo 2. Open frontend: https://your-site-name.netlify.app
echo 3. Register a new user and test functionality
echo.

echo 📋 Quick Reference:
echo ===================
echo GitHub Repo: https://github.com/CrazyCoders1/quizbattle
echo Render: https://render.com
echo Netlify: https://netlify.com
echo Deployment Guide: DEPLOYMENT_CHECKLIST.md
echo.

echo Press any key to open deployment checklist...
pause >nul
start DEPLOYMENT_CHECKLIST.md