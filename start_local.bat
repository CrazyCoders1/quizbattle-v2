@echo off
echo 🚀 Starting QuizBattle Locally (No Docker)
echo ==========================================

echo.
echo 📦 Backend Setup (Flask)
cd backend
echo Installing Python dependencies...
pip install -r requirements.txt
echo.

echo 🌍 Starting Flask backend on http://localhost:5000
echo Press Ctrl+C to stop backend
start cmd /k "flask run"

echo.
echo ⏳ Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo ⚛️ Frontend Setup (React)
cd ..\frontend
echo Installing Node dependencies...
call npm install
echo.

echo 🌍 Starting React frontend on http://localhost:3000
echo Press Ctrl+C to stop frontend
start cmd /k "npm start"

echo.
echo ✅ QuizBattle started successfully!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:5000
echo 💚 Health:   http://localhost:5000/health
echo.
echo Press any key to close this window...
pause >nul