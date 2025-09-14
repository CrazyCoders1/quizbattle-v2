# Test QuizBattle API after database initialization
Write-Host "🧪 Testing QuizBattle API..." -ForegroundColor Cyan

# Test 1: Health check
Write-Host "`n1️⃣  Testing health endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "https://quizbattle-backend.onrender.com/health" -Method GET
    Write-Host "✅ Health check: SUCCESS" -ForegroundColor Green
    Write-Host "Response: $($health | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Health check: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: User registration
Write-Host "`n2️⃣  Testing user registration..." -ForegroundColor Yellow
try {
    $registerBody = @{
        username = "testuser"
        email = "test@test.com"
        password = "test123"
    } | ConvertTo-Json
    
    $register = Invoke-RestMethod -Uri "https://quizbattle-backend.onrender.com/api/auth/register" -Method POST -Headers @{"Content-Type"="application/json"} -Body $registerBody
    Write-Host "✅ User registration: SUCCESS" -ForegroundColor Green
    Write-Host "Response: $($register | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "❌ User registration: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody" -ForegroundColor Red
    }
}

# Test 3: Admin login
Write-Host "`n3️⃣  Testing admin login..." -ForegroundColor Yellow
try {
    $loginBody = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json
    
    $login = Invoke-RestMethod -Uri "https://quizbattle-backend.onrender.com/api/auth/admin-login" -Method POST -Headers @{"Content-Type"="application/json"} -Body $loginBody
    Write-Host "✅ Admin login: SUCCESS" -ForegroundColor Green
    Write-Host "Response: $($login | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Admin login: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n🎯 Test Summary:" -ForegroundColor Cyan
Write-Host "If all tests show ✅ SUCCESS, your database initialization worked!" -ForegroundColor Green
Write-Host "If you still see ❌ FAILED, the database may need manual initialization." -ForegroundColor Yellow
Write-Host "`n🔑 Admin credentials: admin / admin123" -ForegroundColor Magenta
Write-Host "🌐 Frontend URL: https://quizbattle-frontend.netlify.app" -ForegroundColor Magenta