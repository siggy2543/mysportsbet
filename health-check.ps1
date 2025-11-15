# Windows PowerShell Health Monitoring Script
# Monitors the Sports Betting App services and provides status reports

param(
    [switch]$Continuous = $false,
    [int]$IntervalSeconds = 30
)

function Test-ServiceHealth {
    param([string]$ServiceName, [string]$Url, [switch]$SkipCertCheck = $false)
    
    try {
        if ($SkipCertCheck) {
            [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
        }
        
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $ServiceName - Healthy" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️  $ServiceName - Status Code: $($response.StatusCode)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ $ServiceName - Failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-ContainerStatus {
    Write-Host ""
    Write-Host "🐳 Container Status:" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    
    try {
        $containers = docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}"
        $containers | ForEach-Object {
            if ($_ -match "Up") {
                Write-Host $_ -ForegroundColor Green
            } elseif ($_ -match "unhealthy") {
                Write-Host $_ -ForegroundColor Red
            } else {
                Write-Host $_ -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "❌ Failed to get container status: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-DatabaseConnection {
    Write-Host ""
    Write-Host "🗄️  Database Connection:" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan
    
    try {
        $result = docker-compose exec -T postgres pg_isready -h localhost -p 5432
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PostgreSQL - Connected" -ForegroundColor Green
        } else {
            Write-Host "❌ PostgreSQL - Not ready" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ PostgreSQL test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-RedisConnection {
    Write-Host ""
    Write-Host "📦 Redis Connection:" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    
    try {
        $result = docker-compose exec -T redis redis-cli ping
        if ($result -match "PONG") {
            Write-Host "✅ Redis - Connected" -ForegroundColor Green
        } else {
            Write-Host "❌ Redis - Not responding" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Redis test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-CeleryWorkers {
    Write-Host ""
    Write-Host "⚙️  Celery Workers:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    
    try {
        $result = docker-compose exec -T celery-worker celery inspect active
        if ($result -match "1 node online") {
            Write-Host "✅ Celery Worker - Online" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Celery Worker - Status unclear" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Celery worker test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    try {
        $result = docker-compose exec -T celery-beat celery inspect scheduled
        Write-Host "✅ Celery Beat - Scheduler running" -ForegroundColor Green
    } catch {
        Write-Host "❌ Celery beat test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-SystemMetrics {
    Write-Host ""
    Write-Host "📊 System Metrics:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    
    # Docker system info
    try {
        $dockerInfo = docker system df --format "table {{.Type}}\t{{.Total}}\t{{.Active}}\t{{.Size}}"
        Write-Host "Docker Resource Usage:"
        $dockerInfo | ForEach-Object { Write-Host $_ }
    } catch {
        Write-Host "❌ Failed to get Docker metrics" -ForegroundColor Red
    }
    
    # Memory usage
    try {
        $memInfo = Get-WmiObject -Class Win32_OperatingSystem
        $totalMem = [math]::Round($memInfo.TotalVisibleMemorySize / 1MB, 2)
        $freeMem = [math]::Round($memInfo.FreePhysicalMemory / 1MB, 2)
        $usedMem = [math]::Round($totalMem - $freeMem, 2)
        $memPercent = [math]::Round(($usedMem / $totalMem) * 100, 1)
        
        Write-Host "System Memory: $usedMem GB / $totalMem GB ($memPercent% used)" -ForegroundColor Yellow
    } catch {
        Write-Host "X Failed to get memory info" -ForegroundColor Red
    }
}

function Test-APIEndpoints {
    Write-Host ""
    Write-Host "🌐 API Endpoints:" -ForegroundColor Cyan
    Write-Host "================" -ForegroundColor Cyan
    
    # Determine if SSL is enabled
    $sslEnabled = $false
    if (Test-Path "nginx\ssl\fullchain.pem") {
        $sslEnabled = $true
    }
    
    $protocol = if ($sslEnabled) { "https" } else { "http" }
    $skipCert = $sslEnabled
    
    # Test various endpoints
    Test-ServiceHealth "Frontend" "${protocol}://localhost" -SkipCertCheck:$skipCert
    Test-ServiceHealth "API Health" "${protocol}://localhost/health" -SkipCertCheck:$skipCert
    Test-ServiceHealth "API Status" "${protocol}://localhost/api/v1/bets/public/status" -SkipCertCheck:$skipCert
    Test-ServiceHealth "API Docs" "${protocol}://localhost/docs" -SkipCertCheck:$skipCert
    
    # Test betting recommendations (may be empty but should return 200)
    try {
        if ($skipCert) {
            [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
        }
        $response = Invoke-WebRequest -Uri "$protocol://localhost/api/v1/bets/public/recommendations" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Betting Recommendations API - Healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Betting Recommendations API - Failed" -ForegroundColor Red
    }
}

function Show-QuickActions {
    Write-Host ""
    Write-Host "🔧 Quick Actions:" -ForegroundColor Cyan
    Write-Host "================" -ForegroundColor Cyan
    Write-Host "View logs:           docker-compose logs -f [service]"
    Write-Host "Restart service:     docker-compose restart [service]"
    Write-Host "Stop all:           docker-compose down"
    Write-Host "Start all:          docker-compose up -d"
    Write-Host "Rebuild:            docker-compose build --no-cache [service]"
    Write-Host "Shell access:       docker-compose exec [service] /bin/sh"
    Write-Host ""
    Write-Host "SSL Commands:"
    Write-Host "Generate SSL:       ./setup-ssl-windows.bat"
    Write-Host "Start with SSL:     docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d"
}

function Run-HealthCheck {
    Clear-Host
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host " Sports Betting App Health Check" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
    Get-ContainerStatus
    Test-DatabaseConnection
    Test-RedisConnection
    Test-CeleryWorkers
    Test-APIEndpoints
    Show-SystemMetrics
    Show-QuickActions
    
    Write-Host ""
    Write-Host "Health check completed at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
}

# Main execution
if ($Continuous) {
    Write-Host "Starting continuous health monitoring (Ctrl+C to stop)..." -ForegroundColor Yellow
    Write-Host "Interval: $IntervalSeconds seconds" -ForegroundColor Yellow
    
    while ($true) {
        Run-HealthCheck
        Write-Host ""
        Write-Host "Waiting $IntervalSeconds seconds for next check..." -ForegroundColor Gray
        Start-Sleep -Seconds $IntervalSeconds
    }
} else {
    Run-HealthCheck
}

Write-Host ""
Write-Host "For continuous monitoring, use: .\health-check.ps1 -Continuous" -ForegroundColor Yellow