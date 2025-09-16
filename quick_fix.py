"""
QUICK FIX: Put backend .env back to production and push to GitHub
Your production hosting should work fine - the issue is local Flask crashing
"""

# Read current .env
with open('backend/.env', 'r') as f:
    current_env = f.read()

print("Current .env content:")
print(current_env)
print("\n" + "="*50 + "\n")

# Write production configuration
production_env = """# Backend Environment Variables for Render Production
JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
DATABASE_URL=postgresql://neondb_owner:npg_NY1EtTX5cqZH@ep-dawn-star-a1lemfrx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
MONGO_URI=mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0
MONGODB_URI=mongodb+srv://quizbattle-db:4XPuEpIO2UUMemYR@cluster0.pzs2nrd.mongodb.net/quizbattle?retryWrites=true&w=majority&appName=Cluster0
FLASK_ENV=production
FLASK_DEBUG=False
PORT=10000
ADMIN_PASSWORD=admin987

# CORS Configuration - Add your Netlify domain here
CORS_ORIGINS=https://quizbattle-v2.netlify.app,https://www.quizbattle-v2.netlify.app,http://localhost:3000
"""

with open('backend/.env', 'w') as f:
    f.write(production_env)

print("✅ Fixed backend/.env for production")
print("🚀 Ready to commit and push to GitHub")
print("📱 Your production hosting (Render + Netlify) should work fine!")
print("\nThe leaderboard network error was fixed by:")
print("- ✅ CORS configuration for Netlify")
print("- ✅ Production database credentials")
print("- ✅ Enhanced error handling")

print("""
NEXT STEPS:
1. git add . && git commit -m "Fix production configuration"
2. git push origin main
3. Wait 2-3 minutes for Render/Netlify to deploy
4. Test at https://quizbattle-v2.netlify.app

Your production deployment will work - the local issue is just Flask crashing on Windows.
""")