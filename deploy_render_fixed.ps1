# QuizBattle Render Deployment Script
Write-Host "🚀 Deploying QuizBattle Backend to Render..." -ForegroundColor Cyan

# Set API endpoints
$RENDER_API_BASE = "https://api.render.com/v1"
$RENDER_API_KEY = $env:RENDER_API_KEY

if (-not $RENDER_API_KEY) {
    Write-Host "❌ RENDER_API_KEY not found in environment variables" -ForegroundColor Red
    exit 1
}

# Headers for API requests
$headers = @{
    "Authorization" = "Bearer $RENDER_API_KEY"
    "Content-Type" = "application/json"
}

# Create Web Service payload
$servicePayload = @{
    type = "web_service"
    name = "quizbattle-backend"
    repo = "https://github.com/CrazyCoders1/quizbattle"
    branch = "main"
    rootDir = "backend"
    runtime = "python3"
    buildCommand = "pip install --no-cache-dir -r requirements.txt && flask db upgrade"
    startCommand = "gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app"
    plan = "free"
    region = "singapore"
    envVars = @(
        @{
            key = "DATABASE_URL"
            value = "postgresql://neondb_owner:npg_WFb53JDcuAzZ@ep-mute-wave-a1c13882-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        },
        @{
            key = "MONGO_URI"
            value = "mongodb+srv://quizbattle:KITUx2vkIKq4wgJ3@cluster0.tntmlsa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        },
        @{
            key = "JWT_SECRET"
            value = "e57f70fc4fd74a56aa710c40ad11caaa"
        },
        @{
            key = "ADMIN_PASSWORD"
            value = "admin987"
        },
        @{
            key = "FLASK_ENV"
            value = "production"
        },
        @{
            key = "FLASK_APP"
            value = "wsgi.py"
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "📡 Creating Render service..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$RENDER_API_BASE/services" -Method Post -Headers $headers -Body $servicePayload
    
    if ($response.id) {
        Write-Host "✅ Service created successfully!" -ForegroundColor Green
        Write-Host "Service ID: $($response.id)" -ForegroundColor Cyan
        Write-Host "Service URL: https://$($response.name).onrender.com" -ForegroundColor Cyan
        Write-Host "Dashboard: https://dashboard.render.com/web/$($response.id)" -ForegroundColor Cyan
        
        # Save service info for later use
        @{
            service_id = $response.id
            service_url = "https://$($response.name).onrender.com"
            dashboard_url = "https://dashboard.render.com/web/$($response.id)"
        } | ConvertTo-Json | Out-File -FilePath "render_service_info.json"
        
        Write-Host "🎉 Backend deployment initiated! Check the dashboard for build progress." -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create service" -ForegroundColor Red
        Write-Host $response -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error creating Render service:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $errorResponse = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorResponse)
        $errorBody = $reader.ReadToEnd()
        Write-Host "Error details: $errorBody" -ForegroundColor Red
    }
}