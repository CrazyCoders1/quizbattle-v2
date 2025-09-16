# QuizBattle Netlify Deployment Script
Write-Host "🌐 Deploying QuizBattle Frontend to Netlify..." -ForegroundColor Cyan

$NETLIFY_ACCESS_TOKEN = $env:NETLIFY_ACCESS_TOKEN

if (-not $NETLIFY_ACCESS_TOKEN) {
    Write-Host "❌ NETLIFY_ACCESS_TOKEN not found" -ForegroundColor Red
    Write-Host "Please set: `$env:NETLIFY_ACCESS_TOKEN='nfp_UwigJ3RuyQqm54qLwxp7f2Pd48mdCNYwf015'" -ForegroundColor Yellow
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $NETLIFY_ACCESS_TOKEN"
    "Content-Type" = "application/json"
}

# Create site payload
$sitePayload = @{
    name = "quizbattle-frontend"
    build_settings = @{
        base_dir = "frontend"
        cmd = "npm ci && npm run build"
        dir = "build"
    }
} | ConvertTo-Json -Depth 5

Write-Host "📡 Creating Netlify site..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "https://api.netlify.com/api/v1/sites" -Method Post -Headers $headers -Body $sitePayload
    
    Write-Host "✅ Site created successfully!" -ForegroundColor Green
    Write-Host "Site ID: $($response.id)" -ForegroundColor Cyan
    Write-Host "Site URL: $($response.url)" -ForegroundColor Cyan
    Write-Host "Admin URL: $($response.admin_url)" -ForegroundColor Cyan
    
    # Save site info
    @{
        site_id = $response.id
        site_url = $response.url
        admin_url = $response.admin_url
    } | ConvertTo-Json | Out-File -FilePath "netlify_site_info.json"
    
    Write-Host "🎉 Frontend deployment setup complete!" -ForegroundColor Green
    Write-Host "📝 Site info saved to netlify_site_info.json" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor White
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Go to Netlify dashboard and connect your GitHub repository" -ForegroundColor White
    Write-Host "2. Set build directory to 'frontend/build'" -ForegroundColor White
    Write-Host "3. Add environment variable REACT_APP_API_URL" -ForegroundColor White
    
} catch {
    Write-Host "❌ Error creating Netlify site:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}