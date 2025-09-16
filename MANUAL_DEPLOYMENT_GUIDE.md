# 🚀 QuizBattle-v2 Manual Deployment Guide (Latest Versions)

## 📋 **Latest Version Stack**
- **Python**: 3.12.7 (Latest Stable)
- **Node.js**: 22.x (Latest LTS)
- **Flask**: 3.1.0
- **React**: 18.3.1
- **PostgreSQL**: psycopg3 (Latest)
- **MongoDB**: pymongo 4.10.1

---

## 🎯 **Prerequisites Checklist**

### **Accounts Required**
- [ ] GitHub account with repository access
- [ ] Render account (free tier): https://render.com
- [ ] Netlify account (free tier): https://netlify.com
- [ ] Neon PostgreSQL database (configured)
- [ ] MongoDB Atlas cluster (configured)

### **Repository Status**
- ✅ Repository: `https://github.com/CrazyCoders1/quizbattle-v2`
- ✅ Latest code pushed to main branch
- ✅ All configuration files ready

---

## 🔧 **Part 1: Backend Deployment on Render**

### **Step 1.1: Access Render Dashboard**
1. Go to https://dashboard.render.com
2. Sign in with your account
3. Click **"New"** button (top right)

### **Step 1.2: Choose Deployment Method**

#### **🎯 Method A: Blueprint Deployment (Recommended)**
1. Select **"Blueprint"**
2. **Connect GitHub Repository**:
   - Click "Connect GitHub"
   - Authorize Render if needed
   - Search for `quizbattle-v2`
   - Select `CrazyCoders1/quizbattle-v2`
3. **Review Blueprint Configuration**:
   - Render will detect `render.yaml`
   - Review the service configuration
   - All environment variables are pre-configured
4. **Deploy**:
   - Click **"Apply"**
   - Wait for deployment (5-10 minutes)
   - Monitor build logs

#### **🛠️ Method B: Manual Web Service (If Blueprint Fails)**
1. Select **"Web Service"**
2. **Connect Repository**:
   - Click "Connect GitHub"
   - Select `CrazyCoders1/quizbattle-v2`
   - Branch: `main`

3. **Service Configuration**:
   ```
   Service Name: quizbattle-v2-backend
   Region: Oregon (US-West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install --no-cache-dir -r requirements.txt && flask db upgrade
   Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
   Plan: Free
   ```

4. **Environment Variables**:
   Click "Advanced" → "Add Environment Variable" for each:
   ```
   DATABASE_URL = postgresql://neondb_owner:npg_WFb53JDcuAzZ@ep-mute-wave-a1c13882-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   MONGO_URI = mongodb+srv://quizbattle:KITUx2vkIKq4wgJ3@cluster0.tntmlsa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   JWT_SECRET = e57f70fc4fd74a56aa710c40ad11caaa
   ADMIN_PASSWORD = admin987
   FLASK_ENV = production
   FLASK_APP = wsgi.py
   PYTHON_VERSION = 3.11
   ```

5. **Health Check**:
   - Health Check Path: `/health`

6. **Deploy**:
   - Click **"Create Web Service"**
   - Monitor build progress

### **Step 1.3: Verify Backend Deployment**
1. **Wait for Build to Complete** (5-10 minutes)
2. **Note Backend URL**: Something like `https://quizbattle-v2-backend-abc123.onrender.com`
3. **Test Health Check**:
   ```powershell
   curl https://your-backend-url.onrender.com/health
   ```
   Should return: `{"status": "healthy", "timestamp": "...", "version": "1.0.0"}`

4. **Test Admin Login**:
   ```powershell
   curl -X POST https://your-backend-url.onrender.com/api/auth/admin/login `
     -H "Content-Type: application/json" `
     -d '{"username": "admin", "password": "admin987"}'
   ```

---

## 🌐 **Part 2: Frontend Deployment on Netlify**

### **Step 2.1: Access Netlify Dashboard**
1. Go to https://app.netlify.com
2. Sign in with your account
3. Navigate to existing site: https://app.netlify.com/projects/quizbattle-v2-frontend

### **Step 2.2: Connect GitHub Repository**
1. **Site Settings**:
   - Click "Site settings" (left sidebar)
   - Go to "Build & deploy" → "Continuous deployment"
   - Click "Link repository"

2. **Repository Connection**:
   - Choose "GitHub"
   - Authorize Netlify if needed
   - Select `CrazyCoders1/quizbattle-v2`
   - Branch: `main`

### **Step 2.3: Configure Build Settings**
1. **Build Configuration**:
   ```
   Base directory: frontend
   Build command: npm ci && npm run build
   Publish directory: frontend/build
   ```

2. **Advanced Settings**:
   - Node.js version: 22 (auto-detected from netlify.toml)

### **Step 2.4: Set Environment Variables**
1. Go to **"Site settings"** → **"Environment variables"**
2. **Add Variables**:
   - **Variable 1**:
     - Key: `REACT_APP_API_URL`
     - Value: `https://[your-render-backend-url].onrender.com/api`
     - Replace `[your-render-backend-url]` with actual URL from Step 1.3
   - **Variable 2**:
     - Key: `NODE_VERSION`
     - Value: `22`
   - **Variable 3**:
     - Key: `NODE_ENV`
     - Value: `production`

### **Step 2.5: Deploy Frontend**
1. **Trigger Deploy**:
   - Go to "Deploys" tab
   - Click "Deploy site"
   - Or: "Trigger deploy" → "Deploy site"

2. **Monitor Build** (2-5 minutes)
   - Watch build logs
   - Wait for "Site is live" status

3. **Verify Deployment**:
   - Site URL: https://quizbattle-v2-frontend.netlify.app
   - Check if site loads correctly

---

## 🧪 **Part 3: Testing Complete Setup**

### **Step 3.1: Frontend-Backend Integration Test**
1. **Open Frontend**: https://quizbattle-v2-frontend.netlify.app
2. **Test User Registration**:
   - Click "Register"
   - Create a new account
   - Verify registration works
3. **Test User Login**:
   - Login with created account
   - Verify dashboard loads

### **Step 3.2: Admin Panel Test**
1. **Admin Login**:
   - Go to `/admin` or find admin login
   - Username: `admin`
   - Password: `admin987`
2. **Test Admin Features**:
   - Dashboard loads
   - User management visible
   - PDF upload functionality

### **Step 3.3: Core Features Test**
1. **Challenge Creation** (as admin or user):
   - Create a new challenge
   - Set questions and difficulty
   - Verify challenge is created
2. **Challenge Participation**:
   - Join the challenge (different browser/incognito)
   - Take the quiz
   - Submit answers
3. **Results & Leaderboard**:
   - View results after completion
   - Check leaderboard updates

---

## 🛠️ **Troubleshooting Guide**

### **Backend Issues**

#### **Build Failures**
```bash
# Check build logs in Render dashboard
# Common issues and solutions:

# Issue: Python version mismatch
Solution: Verify runtime.txt contains "python-3.12.7"

# Issue: Requirements installation fails
Solution: Check backend/requirements.txt for syntax errors

# Issue: Database migration fails
Solution: Verify DATABASE_URL environment variable
```

#### **Runtime Errors**
```bash
# Health check fails
curl https://your-backend-url.onrender.com/health
# If 404: Check if service is running
# If 500: Check application logs in Render dashboard

# Database connection errors
# Check environment variables in Render dashboard
# Verify Neon database URL is correct and accessible
```

### **Frontend Issues**

#### **Build Failures**
```bash
# Check Netlify build logs
# Common issues:

# Issue: npm install fails
Solution: Verify package.json syntax and dependencies

# Issue: React build fails
Solution: Check for TypeScript errors or missing dependencies

# Issue: Environment variable not found
Solution: Verify REACT_APP_API_URL is set correctly
```

#### **Runtime Issues**
```bash
# Frontend loads but API calls fail
# Check browser developer tools → Network tab
# Common issues:

# CORS errors
Solution: Ensure backend CORS allows frontend domain

# API URL incorrect
Solution: Verify REACT_APP_API_URL in Netlify environment variables

# Backend not responding
Solution: Check backend health at /health endpoint
```

---

## 📊 **Expected Deployment Timeline**

### **Time Estimates**
- **Render Backend Setup**: 10-15 minutes
- **Render Build & Deploy**: 5-10 minutes
- **Netlify Frontend Setup**: 5-10 minutes
- **Netlify Build & Deploy**: 2-5 minutes
- **Testing & Verification**: 10-15 minutes
- **Total Time**: 30-45 minutes

### **Status Indicators**
- ✅ **Backend Ready**: Health check responds at `/health`
- ✅ **Frontend Ready**: Site loads without errors
- ✅ **Integration Ready**: User registration/login works
- ✅ **Fully Functional**: Admin panel and challenges work

---

## 🔄 **Post-Deployment Maintenance**

### **Auto-Deployments**
- **Backend**: Automatic deploy on push to main branch
- **Frontend**: Automatic deploy on push to main branch
- **Monitor**: Check deployment status in dashboards

### **Environment Updates**
- **Render**: Update environment variables in service settings
- **Netlify**: Update environment variables in site settings
- **Database**: Migrations run automatically on backend deploy

### **Monitoring**
- **Backend Health**: https://your-backend-url.onrender.com/health
- **Frontend Status**: https://quizbattle-v2-frontend.netlify.app
- **Logs**: Available in respective dashboards

---

## ✅ **Success Checklist**

Mark each item as complete:

### **Backend Deployment**
- [ ] Render service created and running
- [ ] Health check endpoint responding
- [ ] Database migrations completed
- [ ] Admin login functional
- [ ] Environment variables set correctly

### **Frontend Deployment**  
- [ ] Netlify site deployed successfully
- [ ] Site loads without errors
- [ ] API integration working
- [ ] User registration/login functional
- [ ] Admin panel accessible

### **Full Integration**
- [ ] End-to-end user flow working
- [ ] Challenge creation/participation functional
- [ ] PDF upload working (admin)
- [ ] Leaderboard updating correctly
- [ ] All features tested and working

---

## 📞 **Support Resources**

### **Documentation**
- Render Docs: https://render.com/docs
- Netlify Docs: https://docs.netlify.com
- Flask Docs: https://flask.palletsprojects.com

### **Status Pages**
- Render Status: https://status.render.com
- Netlify Status: https://status.netlify.com

Your QuizBattle application should now be fully deployed and operational! 🎉