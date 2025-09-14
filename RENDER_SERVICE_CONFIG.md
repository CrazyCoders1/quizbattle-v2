# 🔧 Render Service Configuration - Quick Reference

**Problem:** Python version conflicts causing psycopg2 import errors  
**Solution:** Recreate service with proper root directory configuration

---

## 🚀 **New Service Settings**

### **Basic Configuration:**
```
Service Type: Web Service
Repository: CrazyCoders1/quizbattle
Name: quizbattle-backend-v2
Runtime: Python 3
```

### **Build Configuration:**
```
Root Directory: backend
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: gunicorn run:app --bind 0.0.0.0:$PORT
```

### **Environment Variables:**
```
JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
DATABASE_URL=postgresql://neondb_owner:password@ep-crimson-night-a14reavo-pooler.ap-southeast-1.aws.neon.tech/quizbattle?sslmode=require
MONGO_URI=mongodb+srv://quizbattle-db:password@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0
FLASK_ENV=production
PORT=10000
```

---

## 🎯 **Key Changes:**

1. **Root Directory: `backend`** - Eliminates path issues
2. **Simplified commands** - No `cd` commands needed
3. **Updated psycopg2-binary** - Better Python 3.13 compatibility
4. **Clear build cache** - Fresh start with new dependencies

---

## ✅ **Expected Result:**

- ✅ Build successful
- ✅ Deploy successful  
- ✅ Health endpoint working: `https://your-new-url.onrender.com/health`
- ✅ No psycopg2 import errors

This configuration mirrors successful Render deployments and should resolve the Python/PostgreSQL compatibility issues.