# 🎰 Sports Betting App - Live DraftKings Production Deployment (Windows)
# Deploys the app with live betting capabilities on Windows

param(
    [switch]$SkipHealthCheck,
    [switch]$TestConnection
)

Write-Host "Deploying Sports Betting App with Live DraftKings Integration..." -ForegroundColor Magenta

function Write-Header {
    param($Message)
    Write-Host "================================" -ForegroundColor Magenta
    Write-Host " $Message " -ForegroundColor Magenta  
    Write-Host "================================" -ForegroundColor Magenta
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Info {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    exit 1
}

# Check prerequisites
Write-Header "Checking Prerequisites"

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed. Please install Docker Desktop first."
}

if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Error "Docker Compose is not installed. Please install Docker Compose first."
}

try {
    docker info | Out-Null
    Write-Success "Docker is running"
} catch {
    Write-Error "Docker is not running. Please start Docker Desktop first."
}

Write-Success "Docker and Docker Compose are ready"

# Verify environment configuration
Write-Header "Verifying Environment Configuration"

if (!(Test-Path ".env")) {
    Write-Error ".env file not found. Please ensure your environment configuration exists."
}

$envContent = Get-Content ".env" -Raw

if ($envContent -notmatch "DRAFTKINGS_USERNAME=") {
    Write-Error "DRAFTKINGS_USERNAME not found in .env file"
}

if ($envContent -notmatch "DRAFTKINGS_PASSWORD=") {
    Write-Error "DRAFTKINGS_PASSWORD not found in .env file"
}

if ($envContent -notmatch "OPENAI_API_KEY=") {
    Write-Error "OPENAI_API_KEY not found in .env file"
}

Write-Success "Environment configuration verified"

# Create necessary directories
Write-Header "Setting Up Directory Structure"

$directories = @(
    "logs\api",
    "logs\nginx", 
    "logs\postgres",
    "logs\redis",
    "logs\celery",
    "monitoring",
    "nginx\ssl"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

Write-Success "Directory structure created"

# Generate SSL certificates for local deployment
Write-Header "Setting Up SSL Certificates"

if (!(Test-Path "nginx\ssl\server.crt")) {
    Write-Info "Generating self-signed SSL certificates..."
    
    # Create OpenSSL config for Windows
    $opensslConfig = @"
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = MD
L = Baltimore
O = SportsBettingApp
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
"@
    
    $opensslConfig | Out-File -FilePath "nginx\ssl\openssl.conf" -Encoding ASCII
    
    # Generate certificate using Docker (cross-platform)
    docker run --rm -v "${PWD}\nginx\ssl:/certs" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/server.key -out /certs/server.crt -config /certs/openssl.conf
    
    Write-Success "SSL certificates generated"
} else {
    Write-Success "SSL certificates already exist"
}

# Create monitoring configuration
Write-Header "Setting Up Monitoring"

$prometheusConfig = @"
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sports-betting-api'
    static_configs:
      - targets: ['api:8000']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
"@

$prometheusConfig | Out-File -FilePath "monitoring\prometheus.yml" -Encoding UTF8

Write-Success "Monitoring configuration created"

# Build production images
Write-Header "Building Production Docker Images"

Write-Info "Building backend production image..."
docker-compose -f docker-compose.production.yml build api

Write-Info "Building frontend production image..."
docker-compose -f docker-compose.production.yml build frontend

Write-Success "Production images built successfully"

# Stop any existing containers
Write-Header "Stopping Existing Containers"

docker-compose down --remove-orphans 2>$null
docker-compose -f docker-compose.production.yml down --remove-orphans 2>$null

Write-Success "Existing containers stopped"

# Deploy production stack
Write-Header "Deploying Production Stack"

Write-Info "Starting production services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
Write-Info "Waiting for services to start..."
Start-Sleep -Seconds 30

# Health checks
if (!$SkipHealthCheck) {
    Write-Header "Running Health Checks"

    Write-Info "Checking API health..."
    $healthCheckPassed = $false
    for ($i = 1; $i -le 10; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "https://localhost/api/v1/bets/public/status" -SkipCertificateCheck -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Success "API is responding"
                $healthCheckPassed = $true
                break
            }
        } catch {
            # Continue trying
        }
        
        if ($i -eq 10) {
            Write-Error "API health check failed after 10 attempts"
        }
        Start-Sleep -Seconds 5
    }

    Write-Info "Checking frontend..."
    try {
        $response = Invoke-WebRequest -Uri "https://localhost" -SkipCertificateCheck -TimeoutSec 5
        Write-Success "Frontend is serving"
    } catch {
        Write-Warning "Frontend may not be ready yet"
    }

    Write-Info "Checking database connection..."
    $pgReady = docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U sportsapp
    if ($pgReady -match "accepting connections") {
        Write-Success "Database is ready"
    } else {
        Write-Warning "Database connection check failed"
    }
}

# Verify DraftKings integration
Write-Header "Verifying DraftKings Integration"

Write-Info "Testing DraftKings service connection..."
Start-Sleep -Seconds 10

# Check if betting services are running
$apiLogs = docker-compose -f docker-compose.production.yml logs api
if ($apiLogs -match "DraftKings") {
    Write-Success "DraftKings service initialized"
} else {
    Write-Warning "DraftKings service logs not found - check manual connection"
}

# Display deployment summary
Write-Header "Deployment Summary"

Write-Host "Sports Betting App is now live with DraftKings integration!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Access Points:" -ForegroundColor Blue
Write-Host "   Dashboard:     https://localhost/" -ForegroundColor Yellow
Write-Host "   API Status:    https://localhost/api/v1/bets/public/status" -ForegroundColor Yellow
Write-Host "   API Docs:      https://localhost/docs" -ForegroundColor Yellow
Write-Host "   Monitoring:    http://localhost:9090" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎯 Betting Configuration:" -ForegroundColor Blue
Write-Host "   Account:       siggy2543@gmail.com" -ForegroundColor Yellow
Write-Host "   State:         Maryland (MD)" -ForegroundColor Yellow
Write-Host "   Bet Amount:    `$5.00 per bet" -ForegroundColor Yellow
Write-Host "   Daily Limit:   `$500.00" -ForegroundColor Yellow
Write-Host "   Auto Betting:  ENABLED" -ForegroundColor Yellow
Write-Host ""
Write-Host "📈 Expected Performance:" -ForegroundColor Blue
Write-Host "   Bets/Day:      5-15 high-confidence bets" -ForegroundColor Yellow
Write-Host "   Investment:    `$25-75 per day" -ForegroundColor Yellow
Write-Host "   Target ROI:    5-10% monthly" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔍 Monitoring Commands:" -ForegroundColor Blue
Write-Host "   View Logs:     docker-compose -f docker-compose.production.yml logs -f api" -ForegroundColor Yellow
Write-Host "   Check Status:  curl -k https://localhost/api/v1/bets/public/status" -ForegroundColor Yellow
Write-Host "   View Bets:     curl -k https://localhost/api/v1/bets/active" -ForegroundColor Yellow
Write-Host ""

# Check if containers are running
Write-Info "Verifying all services are running..."
docker-compose -f docker-compose.production.yml ps

Write-Host ""
Write-Warning "⚠️  IMPORTANT REMINDERS:"
Write-Host "   • Start with small amounts (`$5 bets as configured)" -ForegroundColor White
Write-Host "   • Monitor betting activity closely via dashboard" -ForegroundColor White
Write-Host "   • Ensure sports betting is legal in Maryland" -ForegroundColor White
Write-Host "   • Review and adjust risk management settings as needed" -ForegroundColor White
Write-Host "   • Keep your DraftKings account funded" -ForegroundColor White

Write-Host ""
Write-Success "Production deployment complete! Your betting bot is ready to start placing bets."

# Optional: Run a test bet
if ($TestConnection) {
    Write-Info "Testing DraftKings connection..."
    try {
        $testResponse = Invoke-WebRequest -Uri "https://localhost/api/v1/draftkings/test-connection" -Method Post -SkipCertificateCheck
        Write-Success "DraftKings connection test completed"
    } catch {
        Write-Warning "Test connection failed - check credentials"
    }
}

Write-Success "Deployment script completed successfully!"