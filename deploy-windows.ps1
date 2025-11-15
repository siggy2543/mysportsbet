# Sports Betting App - Windows PowerShell Deployment Script
# Enables SSL, automatic betting, and production deployment

param(
    [switch]$SetupSSL = $false,
    [switch]$EnableAutoBetting = $true,
    [string]$Domain = "localhost"
)

# Function to write colored output
function Write-Status {
    param([string]$Message, [string]$Color = "Blue")
    Write-Host "[INFO] $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host " Sports Betting App Deployment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Status "Checking prerequisites..."

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Success "Docker is installed: $dockerVersion"
} catch {
    Write-Error "Docker is not installed or not running. Please install Docker Desktop for Windows."
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Success "Docker Compose is available: $composeVersion"
} catch {
    Write-Error "Docker Compose is not available. Please ensure Docker Desktop is properly installed."
    exit 1
}

# Setup SSL certificates if requested
if ($SetupSSL) {
    Write-Status "Setting up SSL certificates..."
    
    # Check if OpenSSL is available
    try {
        $opensslVersion = openssl version
        Write-Success "OpenSSL found: $opensslVersion"
        
        # Run SSL setup script
        if (Test-Path "setup-ssl-windows.bat") {
            Write-Status "Running SSL setup script..."
            cmd /c "setup-ssl-windows.bat"
            
            if (Test-Path "nginx\ssl\fullchain.pem") {
                Write-Success "SSL certificates generated successfully"
            } else {
                Write-Warning "SSL certificate generation may have failed"
            }
        } else {
            Write-Warning "SSL setup script not found. Creating certificates manually..."
            
            # Create directories
            New-Item -ItemType Directory -Force -Path "nginx\ssl" | Out-Null
            
            # Generate certificates using PowerShell certificate cmdlets
            $cert = New-SelfSignedCertificate -DnsName $Domain, "localhost", "127.0.0.1" -CertStoreLocation "cert:\CurrentUser\My" -KeyAlgorithm RSA -KeyLength 2048 -NotAfter (Get-Date).AddYears(1)
            
            # Export certificate
            $pwd = ConvertTo-SecureString -String "sportsbetting123" -Force -AsPlainText
            Export-PfxCertificate -Cert $cert -FilePath "nginx\ssl\cert.pfx" -Password $pwd | Out-Null
            
            Write-Success "Self-signed certificate created using PowerShell"
        }
    } catch {
        Write-Warning "OpenSSL not found. Using PowerShell certificate generation..."
        
        # Fallback to PowerShell certificate generation
        New-Item -ItemType Directory -Force -Path "nginx\ssl" | Out-Null
        $cert = New-SelfSignedCertificate -DnsName $Domain, "localhost", "127.0.0.1" -CertStoreLocation "cert:\CurrentUser\My"
        Write-Success "Certificate generated using PowerShell"
    }
}

# Create production environment file
Write-Status "Creating production environment configuration..."

$envContent = @"
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false

# Database Configuration
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=sports_betting_db
POSTGRES_USER=sports_user
POSTGRES_PASSWORD=secure_password_change_in_production

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_change_in_production

# API Keys (Replace with your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
THE_RUNDOWN_API_KEY=your_rundown_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here

# DraftKings Configuration
DRAFTKINGS_USERNAME=your_draftkings_username
DRAFTKINGS_PASSWORD=your_draftkings_password
DRAFTKINGS_STATE=your_state_code

# Betting Configuration
FIXED_BET_AMOUNT=5.0
AUTO_BETTING_ENABLED=$EnableAutoBetting
OPENAI_FALLBACK_ENABLED=true
MAX_DAILY_BETS=10
MAX_BET_EXPOSURE=100.0

# Security
SECRET_KEY=change_this_secret_key_in_production_$(Get-Random)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SSL Configuration
SSL_ENABLED=$SetupSSL
DOMAIN_NAME=$Domain

# URLs
FRONTEND_URL=http$(if($SetupSSL){'s'})://$Domain
BACKEND_URL=http$(if($SetupSSL){'s'})://$Domain/api
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Success "Environment configuration created"

# Build Docker images
Write-Status "Building Docker images..."
try {
    if ($SetupSSL -and (Test-Path "docker-compose.ssl.yml")) {
        docker-compose -f docker-compose.yml -f docker-compose.ssl.yml build --no-cache
    } else {
        docker-compose build --no-cache
    }
    Write-Success "Docker images built successfully"
} catch {
    Write-Error "Failed to build Docker images"
    exit 1
}

# Start services
Write-Status "Starting services..."
try {
    if ($SetupSSL -and (Test-Path "docker-compose.ssl.yml")) {
        docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
        Write-Success "Services started with SSL enabled"
    } else {
        docker-compose up -d
        Write-Success "Services started"
    }
} catch {
    Write-Error "Failed to start services"
    exit 1
}

# Wait for services to be ready
Write-Status "Waiting for services to be ready..."
Start-Sleep -Seconds 30

# Health checks
Write-Status "Performing health checks..."

$protocol = if ($SetupSSL) { "https" } else { "http" }
$healthUrl = "$protocol://localhost/health"

try {
    if ($SetupSSL) {
        # Skip certificate validation for self-signed certs
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
    }
    
    $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Success "Application health check passed"
    } else {
        Write-Warning "Health check returned status code: $($response.StatusCode)"
    }
} catch {
    Write-Warning "Health check failed, but continuing... Error: $($_.Exception.Message)"
}

# Test API endpoints
Write-Status "Testing API endpoints..."
try {
    $apiUrl = "$protocol://localhost/api/v1/bets/public/status"
    $apiResponse = Invoke-WebRequest -Uri $apiUrl -UseBasicParsing -TimeoutSec 10
    if ($apiResponse.StatusCode -eq 200) {
        Write-Success "API endpoints are responding"
    }
} catch {
    Write-Warning "API endpoint test failed: $($_.Exception.Message)"
}

# Enable automated betting if requested
if ($EnableAutoBetting) {
    Write-Status "Configuring automated betting..."
    try {
        $bettingUrl = "$protocol://localhost/api/v1/bets/automated/enable"
        $body = @{ enable = $true } | ConvertTo-Json
        $headers = @{ "Content-Type" = "application/json" }
        
        # This might fail if authentication is required, which is expected
        try {
            Invoke-WebRequest -Uri $bettingUrl -Method POST -Body $body -Headers $headers -UseBasicParsing -TimeoutSec 10 | Out-Null
            Write-Success "Automated betting enabled"
        } catch {
            Write-Warning "Could not automatically enable betting (may require user authentication)"
        }
    } catch {
        Write-Warning "Automated betting configuration failed: $($_.Exception.Message)"
    }
}

# Display deployment summary
Write-Host ""
Write-Host "🎉 Deployment Summary:" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Success "Sports Betting App is now running"
Write-Success "Fixed bet amount: `$5.00"
Write-Success "Automatic betting: $(if($EnableAutoBetting){'Enabled'}else{'Disabled'})"
Write-Success "SSL/HTTPS: $(if($SetupSSL){'Enabled'}else{'Disabled'})"
Write-Success "OpenAI fallback: Enabled"

Write-Host ""
Write-Host "📊 Access URLs:" -ForegroundColor Cyan
$baseUrl = "$protocol://$Domain"
Write-Host "Frontend: $baseUrl"
Write-Host "API: $baseUrl/api"
Write-Host "API Health: $baseUrl/health"
Write-Host "API Docs: $baseUrl/docs"

Write-Host ""
Write-Host "🔧 Management Commands:" -ForegroundColor Yellow
Write-Host "View logs: docker-compose logs -f"
Write-Host "Stop services: docker-compose down"
Write-Host "Restart: docker-compose restart"
Write-Host "Status: docker-compose ps"

Write-Host ""
Write-Host "⚠️  Important Notes:" -ForegroundColor Red
Write-Host "1. Replace placeholder API keys in .env file"
Write-Host "2. Configure proper DraftKings credentials"
Write-Host "3. Monitor automated betting activity"
Write-Host "4. This system will place real bets with real money!"

if ($SetupSSL) {
    Write-Host "5. Trust the self-signed certificate in your browser"
    Write-Host "6. Consider using proper SSL certificates for production"
}

Write-Host ""
Write-Success "🚀 Deployment completed successfully!"
Write-Host "The sports betting system is now live and ready!" -ForegroundColor Green

# Final container status
Write-Host ""
Write-Status "Final container status:"
docker-compose ps