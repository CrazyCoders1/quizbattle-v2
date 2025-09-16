# QuizBattle Netlify Deployment Script
Write-Host "🌐 Deploying QuizBattle Frontend to Netlify..." -ForegroundColor Cyan

# Set API endpoints
$NETLIFY_API_BASE = "https://api.netlify.com/api/v1"
$NETLIFY_ACCESS_TOKEN = $env:NETLIFY_ACCESS_TOKEN

if (-not $NETLIFY_ACCESS_TOKEN) {
    Write-Host "❌ NETLIFY_ACCESS_TOKEN not found in environment variables" -ForegroundColor Red
    exit 1
}

# Headers for API requests
$headers = @{
    "Authorization" = "Bearer $NETLIFY_ACCESS_TOKEN"
    "Content-Type" = "application/json"
}

Write-Host "📡 Creating Netlify site..." -ForegroundColor Yellow

# Create site payload
$sitePayload = @{
    name = "quizbattle-frontend"
    repo = @{
        repo = "https://github.com/CrazyCoders1/quizbattle"
        branch = "main"
        dir = "frontend"
    }
    build_settings = @{
        cmd = "npm ci; npm run build"
        dir = "build"
        base_dir = "frontend"
    }
} | ConvertTo-Json -Depth 10

try {
    # Create site
    $response = Invoke-RestMethod -Uri "$NETLIFY_API_BASE/sites" -Method Post -Headers $headers -Body $sitePayload
    
    if ($response.id) {
        Write-Host "✅ Site created successfully!" -ForegroundColor Green
        Write-Host "Site ID: $($response.id)" -ForegroundColor Cyan
        Write-Host "Site URL: $($response.url)" -ForegroundColor Cyan
        Write-Host "Admin URL: $($response.admin_url)" -ForegroundColor Cyan
        
        $siteId = $response.id
        $siteUrl = $response.url
        
        Write-Host "🔧 Setting up build hook..." -ForegroundColor Yellow
        
        # Set up environment variables
        $envVars = @{
            REACT_APP_API_URL = "https://quizbattle-backend.onrender.com/api"
            NODE_VERSION = "18"
            NODE_ENV = "production"
        }
        
        foreach ($envVar in $envVars.GetEnumerator()) {
            $envPayload = @{
                key = $envVar.Key
                value = $envVar.Value
                scopes = @("builds", "functions")
            } | ConvertTo-Json -Depth 3
            
            try {
                $envResponse = Invoke-RestMethod -Uri "$NETLIFY_API_BASE/accounts/env" -Method Post -Headers $headers -Body $envPayload
                Write-Host "✅ Set environment variable: $($envVar.Key)" -ForegroundColor Green
            }
            catch {
                Write-Host "⚠️ Could not set environment variable $($envVar.Key): $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
        
        # Trigger initial deploy
        Write-Host "🚀 Triggering initial deployment..." -ForegroundColor Yellow
        
        try {
            $deployResponse = Invoke-RestMethod -Uri "$NETLIFY_API_BASE/sites/$siteId/deploys" -Method Post -Headers $headers -Body "{}"
            Write-Host "✅ Deployment triggered! ID: $($deployResponse.id)" -ForegroundColor Green
            Write-Host "📊 Monitor deployment at: $($response.admin_url)" -ForegroundColor Cyan
        }
        catch {
            Write-Host "⚠️ Could not trigger deployment, but site is created. Deploy manually from dashboard." -ForegroundColor Yellow
        }
        
        # Save site info
        @{
            site_id = $response.id
            site_url = $response.url
            admin_url = $response.admin_url
            api_url = $envVars.REACT_APP_API_URL
        } | ConvertTo-Json | Out-File -FilePath "netlify_site_info.json"
        
        Write-Host "🎉 Frontend deployment setup complete!" -ForegroundColor Green
        Write-Host "📝 Site info saved to netlify_site_info.json" -ForegroundColor Cyan
    }
    else {
        Write-Host "❌ Failed to create site" -ForegroundColor Red
        Write-Host $response -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ Error creating Netlify site:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $errorResponse = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorResponse)
        $errorBody = $reader.ReadToEnd()
        Write-Host "Error details: $errorBody" -ForegroundColor Red
    }
}
